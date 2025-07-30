from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

"""
Implementation of a langgraph checkpoint saver using Redis.
Info: https://github.com/redis-developer/langgraph-redis/blob/main/examples/persistence_redis.ipynb
"""
from contextlib import asynccontextmanager, contextmanager
from typing import (
    Any,
    AsyncGenerator,
    AsyncIterator,
    Iterator,
    List,
    Optional,
    Tuple,
)

from langchain_core.runnables import RunnableConfig

from langgraph.checkpoint.base import (
    WRITES_IDX_MAP,
    BaseCheckpointSaver,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    PendingWrite,
    get_checkpoint_id,
)
from langgraph.checkpoint.serde.base import SerializerProtocol
from redis import Redis
from redis.asyncio import Redis as AsyncRedis

REDIS_KEY_SEPARATOR = "$"

# Utilities shared by both RedisSaver and AsyncRedisSaver

def _make_redis_checkpoint_key(
    thread_id: str, checkpoint_ns: str, checkpoint_id: str
) -> str:
    """
    Generate a Redis key for a checkpoint.

    Args:
        thread_id (str): The thread identifier.
        checkpoint_ns (str): The namespace of the checkpoint.
        checkpoint_id (str): The unique identifier of the checkpoint.

    Returns:
        str: The generated Redis key for the checkpoint.
    """
    return REDIS_KEY_SEPARATOR.join(
        ["checkpoint", thread_id, checkpoint_ns, checkpoint_id]
    )

def _make_redis_checkpoint_writes_key(
    thread_id: str,
    checkpoint_ns: str,
    checkpoint_id: str,
    task_id: str,
    idx: Optional[int],
) -> str:
    """
    Generate a Redis key for checkpoint writes.

    Args:
        thread_id (str): The thread identifier.
        checkpoint_ns (str): The namespace of the checkpoint.
        checkpoint_id (str): The unique identifier of the checkpoint.
        task_id (str): The task identifier.
        idx (Optional[int]): The index of the write, if applicable.

    Returns:
        str: The generated Redis key for the checkpoint writes.
    """
    if idx is None:
        return REDIS_KEY_SEPARATOR.join(
            ["writes", thread_id, checkpoint_ns, checkpoint_id, task_id]
        )

    return REDIS_KEY_SEPARATOR.join(
        ["writes", thread_id, checkpoint_ns, checkpoint_id, task_id, str(idx)]
    )


def _parse_redis_checkpoint_key(redis_key: str) -> dict:
    """
    Parse a Redis checkpoint key into its components.

    Args:
        redis_key (str): The Redis key to parse.

    Returns:
        dict: A dictionary containing the parsed components:
            - thread_id (str): The thread identifier.
            - checkpoint_ns (str): The namespace of the checkpoint.
            - checkpoint_id (str): The unique identifier of the checkpoint.

    Raises:
        ValueError: If the key does not start with 'checkpoint'.
    """
    namespace, thread_id, checkpoint_ns, checkpoint_id = redis_key.split(
        REDIS_KEY_SEPARATOR
    )
    if namespace != "checkpoint":
        raise ValueError("Expected checkpoint key to start with 'checkpoint'")

    return {
        "thread_id": thread_id,
        "checkpoint_ns": checkpoint_ns,
        "checkpoint_id": checkpoint_id,
    }


def _parse_redis_checkpoint_writes_key(redis_key: str) -> dict:
    """
    Parse a Redis checkpoint writes key into its components.

    Args:
        redis_key (str): The Redis key to parse.

    Returns:
        dict: A dictionary containing the parsed components:
            - thread_id (str): The thread identifier.
            - checkpoint_ns (str): The namespace of the checkpoint.
            - checkpoint_id (str): The unique identifier of the checkpoint.
            - task_id (str): The task identifier.
            - idx (str): The index of the write.

    Raises:
        ValueError: If the key does not start with 'writes'.
    """
    namespace, thread_id, checkpoint_ns, checkpoint_id, task_id, idx = redis_key.split(
        REDIS_KEY_SEPARATOR
    )
    if namespace != "writes":
        raise ValueError("Expected checkpoint key to start with 'writes'")

    return {
        "thread_id": thread_id,
        "checkpoint_ns": checkpoint_ns,
        "checkpoint_id": checkpoint_id,
        "task_id": task_id,
        "idx": idx,
    }


def _filter_keys(
    keys: List[str], before: Optional[RunnableConfig], limit: Optional[int]
) -> list:
    """
    Filter and sort Redis keys based on optional criteria.

    Args:
        keys (List[str]): The list of Redis keys to filter and sort.
        before (Optional[RunnableConfig]): Configuration to filter keys before a specific checkpoint ID.
        limit (Optional[int]): The maximum number of keys to return.

    Returns:
        list: The filtered and sorted list of Redis keys.
    """
    if before:
        keys = [
            k
            for k in keys
            if (
                _parse_redis_checkpoint_key(k.decode())["checkpoint_id"]  # type: ignore
                < (before.get("configurable", {}).get("checkpoint_id") if before and before.get("configurable") else "")
            )
        ]

    keys = sorted(
        keys,
        key=lambda k: _parse_redis_checkpoint_key(k.decode())["checkpoint_id"], # type: ignore
        reverse=True,
    )
    if limit:
        keys = keys[:limit]
    return keys


def _load_writes(
    serde: SerializerProtocol, task_id_to_data: dict[tuple[str, str], dict]
) -> list[PendingWrite]:
    """
    Deserialize pending writes.

    Args:
        serde (SerializerProtocol): The serializer protocol to use for deserialization.
        task_id_to_data (dict[tuple[str, str], dict]): A mapping of task IDs and data.

    Returns:
        list[PendingWrite]: A list of deserialized pending writes.
    """
    writes = [
        (
            task_id,
            data[b"channel"].decode(),
            serde.loads_typed((data[b"type"].decode(), data[b"value"])),
        )
        for (task_id, _), data in task_id_to_data.items()
    ]
    return writes

def _parse_redis_checkpoint_data(
    serde: SerializerProtocol,
    key: str,
    data: dict,
    pending_writes: Optional[List[PendingWrite]] = None,
) -> Optional[CheckpointTuple]:
    """
    Parse checkpoint data retrieved from Redis.

    Args:
        serde (SerializerProtocol): The serializer protocol to use for deserialization.
        key (str): The Redis key of the checkpoint.
        data (dict): The checkpoint data retrieved from Redis.
        pending_writes (Optional[List[PendingWrite]]): A list of pending writes, if any.

    Returns:
        Optional[CheckpointTuple]: The parsed checkpoint tuple, or None if the data is empty.
    """
    if not data:
        return None

    parsed_key = _parse_redis_checkpoint_key(key)
    thread_id = parsed_key["thread_id"]
    checkpoint_ns = parsed_key["checkpoint_ns"]
    checkpoint_id = parsed_key["checkpoint_id"]
    config = {
        "configurable": {
            "thread_id": thread_id,
            "checkpoint_ns": checkpoint_ns,
            "checkpoint_id": checkpoint_id,
        }
    }

    checkpoint = serde.loads_typed((data[b"type"].decode(), data[b"checkpoint"]))
    metadata = serde.loads(data[b"metadata"].decode())
    parent_checkpoint_id = data.get(b"parent_checkpoint_id", b"").decode()
    parent_config = (
        {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": parent_checkpoint_id,
            }
        }
        if parent_checkpoint_id
        else None
    )
    return CheckpointTuple(
        config=config, # type: ignore
        checkpoint=checkpoint,
        metadata=metadata,
        parent_config=parent_config, # type: ignore
        pending_writes=pending_writes,
    )

class AsyncRedisSaver(BaseCheckpointSaver):
    """Async redis-based checkpoint saver implementation."""

    conn: AsyncRedis

    def __init__(self, conn: AsyncRedis):
        super().__init__()
        self.conn = conn

    @classmethod
    @asynccontextmanager
    async def from_conn_info(
        cls, *, host: str, port: int, db: int
    ) -> AsyncIterator["AsyncRedisSaver"]:
        conn = None
        try:
            conn = AsyncRedis(host=host, port=port, db=db)
            yield AsyncRedisSaver(conn)
        finally:
            if conn:
                await conn.aclose()

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        """Save a checkpoint to the database asynchronously.

        This method saves a checkpoint to Redis. The checkpoint is associated
        with the provided config and its parent config (if any).

        Args:
            config (RunnableConfig): The config to associate with the checkpoint.
            checkpoint (Checkpoint): The checkpoint to save.
            metadata (CheckpointMetadata): Additional metadata to save with the checkpoint.
            new_versions (ChannelVersions): New channel versions as of this write.

        Returns:
            RunnableConfig: Updated configuration after storing the checkpoint.
        """
        thread_id = config["configurable"]["thread_id"] # type: ignore
        checkpoint_ns = config["configurable"]["checkpoint_ns"] # type: ignore
        checkpoint_id = checkpoint["id"]
        parent_checkpoint_id = (
            config.get("configurable", {}).get("checkpoint_id")
            if config.get("configurable") is not None
            else None
        )
        key = _make_redis_checkpoint_key(thread_id, checkpoint_ns, checkpoint_id)

        type_, serialized_checkpoint = self.serde.dumps_typed(checkpoint)
        serialized_metadata = self.serde.dumps(metadata)
        data = {
            "checkpoint": serialized_checkpoint,
            "type": type_,
            "checkpoint_id": checkpoint_id,
            "metadata": serialized_metadata,
            "parent_checkpoint_id": parent_checkpoint_id
            if parent_checkpoint_id
            else "",
        }

        await self.conn.hset(key, mapping=data) # type: ignore
        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
            }
        }

    async def aput_writes( # type: ignore
        self,
        config: RunnableConfig,
        writes: List[Tuple[str, Any]],
        task_id: str,
    ):
        """Store intermediate writes linked to a checkpoint asynchronously.

        This method saves intermediate writes associated with a checkpoint to the database.

        Args:
            config (RunnableConfig): Configuration of the related checkpoint.
            writes (Sequence[Tuple[str, Any]]): List of writes to store, each as (channel, value) pair.
            task_id (str): Identifier for the task creating the writes.
        """
        thread_id = config["configurable"]["thread_id"] # type: ignore
        checkpoint_ns = config["configurable"]["checkpoint_ns"] # type: ignore
        checkpoint_id = config["configurable"]["checkpoint_id"] # type: ignore

        for idx, (channel, value) in enumerate(writes):
            key = _make_redis_checkpoint_writes_key(
                thread_id,
                checkpoint_ns,
                checkpoint_id,
                task_id,
                WRITES_IDX_MAP.get(channel, idx),
            )
            type_, serialized_value = self.serde.dumps_typed(value)
            data = {"channel": channel, "type": type_, "value": serialized_value}
            if all(w[0] in WRITES_IDX_MAP for w in writes):
                # Use HSET which will overwrite existing values
                await self.conn.hset(key, mapping=data) # type: ignore
            else:
                # Use HSETNX which will not overwrite existing values
                for field, value in data.items():
                    await self.conn.hsetnx(key, field, value) # type: ignore

    async def aget_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """Get a checkpoint tuple from Redis asynchronously.

        This method retrieves a checkpoint tuple from Redis based on the
        provided config. If the config contains a "checkpoint_id" key, the checkpoint with
        the matching thread ID and checkpoint ID is retrieved. Otherwise, the latest checkpoint
        for the given thread ID is retrieved.

        Args:
            config (RunnableConfig): The config to use for retrieving the checkpoint.

        Returns:
            Optional[CheckpointTuple]: The retrieved checkpoint tuple, or None if no matching checkpoint was found.
        """
        thread_id = config["configurable"]["thread_id"] # type: ignore
        checkpoint_id = get_checkpoint_id(config)
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "") # type: ignore

        checkpoint_key = await self._aget_checkpoint_key(
            self.conn, thread_id, checkpoint_ns, checkpoint_id
        )
        if not checkpoint_key:
            return None
        checkpoint_data = await self.conn.hgetall(checkpoint_key) # type: ignore

        # load pending writes
        checkpoint_id = (
            checkpoint_id
            or _parse_redis_checkpoint_key(checkpoint_key)["checkpoint_id"]
        )
        pending_writes = await self._aload_pending_writes(
            thread_id, checkpoint_ns, checkpoint_id
        )
        return _parse_redis_checkpoint_data(
            self.serde, checkpoint_key, checkpoint_data, pending_writes=pending_writes
        )

    async def alist(
        self,
        config: Optional[RunnableConfig],
        *,
        # TODO: implement filtering
        filter: Optional[dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> AsyncGenerator[CheckpointTuple, None]:
        """List checkpoints from Redis asynchronously.

        This method retrieves a list of checkpoint tuples from Redis based
        on the provided config. The checkpoints are ordered by checkpoint ID in descending order (newest first).

        Args:
            config (Optional[RunnableConfig]): Base configuration for filtering checkpoints.
            filter (Optional[Dict[str, Any]]): Additional filtering criteria for metadata.
            before (Optional[RunnableConfig]): If provided, only checkpoints before the specified checkpoint ID are returned. Defaults to None.
            limit (Optional[int]): Maximum number of checkpoints to return.

        Yields:
            AsyncIterator[CheckpointTuple]: An asynchronous iterator of matching checkpoint tuples.
        """
        thread_id = config["configurable"]["thread_id"] # type: ignore
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "") # type: ignore
        pattern = _make_redis_checkpoint_key(thread_id, checkpoint_ns, "*")
        keys = _filter_keys(await self.conn.keys(pattern), before, limit)
        for key in keys:
            data = await self.conn.hgetall(key) # type: ignore
            if data and b"checkpoint" in data and b"metadata" in data:
                checkpoint_id = _parse_redis_checkpoint_key(key.decode())[
                    "checkpoint_id"
                ]
                pending_writes = await self._aload_pending_writes(
                    thread_id, checkpoint_ns, checkpoint_id
                )
                yield _parse_redis_checkpoint_data(
                    self.serde, key.decode(), data, pending_writes=pending_writes
                ) # type: ignore

    async def _aload_pending_writes(
        self, thread_id: str, checkpoint_ns: str, checkpoint_id: str
    ) -> List[PendingWrite]:
        """
        Asynchronously load pending writes for a specific checkpoint.

        This method retrieves all pending writes associated with a given checkpoint
        from Redis, parses their keys, and deserializes their data.

        Args:
            thread_id (str): The thread identifier.
            checkpoint_ns (str): The namespace of the checkpoint.
            checkpoint_id (str): The unique identifier of the checkpoint.

        Returns:
            List[PendingWrite]: A list of deserialized pending writes.
        """
        writes_key = _make_redis_checkpoint_writes_key(
            thread_id, checkpoint_ns, checkpoint_id, "*", None
        )
        matching_keys = await self.conn.keys(pattern=writes_key)
        parsed_keys = [
            _parse_redis_checkpoint_writes_key(key.decode()) for key in matching_keys
        ]
        pending_writes = _load_writes(
            self.serde,
            {
                (parsed_key["task_id"], parsed_key["idx"]): await self.conn.hgetall(key) # type: ignore
                for key, parsed_key in sorted(
                    zip(matching_keys, parsed_keys), key=lambda x: x[1]["idx"]
                )
            },
        )
        return pending_writes

    async def _aget_checkpoint_key(
        self, conn, thread_id: str, checkpoint_ns: str, checkpoint_id: Optional[str]
    ) -> Optional[str]:
        """
        Asynchronously determine the Redis key for a checkpoint.

        This method retrieves the Redis key for a specific checkpoint. If a checkpoint ID
        is provided, it generates the key directly. Otherwise, it retrieves the latest
        checkpoint key for the given thread and namespace.

        Args:
            conn: The Redis connection instance.
            thread_id (str): The thread identifier.
            checkpoint_ns (str): The namespace of the checkpoint.
            checkpoint_id (Optional[str]): The unique identifier of the checkpoint, if available.

        Returns:
            Optional[str]: The Redis key for the checkpoint, or None if no matching key is found.
        """
        if checkpoint_id:
            return _make_redis_checkpoint_key(thread_id, checkpoint_ns, checkpoint_id)

        all_keys = await conn.keys(
            _make_redis_checkpoint_key(thread_id, checkpoint_ns, "*")
        )
        if not all_keys:
            return None

        latest_key = max(
            all_keys,
            key=lambda k: _parse_redis_checkpoint_key(k.decode())["checkpoint_id"],
        )
        return latest_key.decode()

class RedisSaver(BaseCheckpointSaver):
    """
    Redis-based checkpoint saver implementation.
    This class provides methods to save and retrieve checkpoints from a Redis database.
    It supports both synchronous and asynchronous operations.
    It uses the Redis client to store checkpoints and their associated metadata.
    It also supports storing intermediate writes linked to checkpoints.
    It is designed to work with the langgraph framework.
    """

    conn: Redis

    def __init__(self, conn: Redis):
        super().__init__()
        self.conn = conn

    @classmethod
    @contextmanager
    def from_conn_info(cls, *, host: str, port: int, db: int) -> Iterator["RedisSaver"]:
        conn = None
        try:
            conn = Redis(host=host, port=port, db=db)
            yield RedisSaver(conn)
        finally:
            if conn:
                conn.close()

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        """Save a checkpoint to Redis.

        Args:
            config (RunnableConfig): The config to associate with the checkpoint.
            checkpoint (Checkpoint): The checkpoint to save.
            metadata (CheckpointMetadata): Additional metadata to save with the checkpoint.
            new_versions (ChannelVersions): New channel versions as of this write.

        Returns:
            RunnableConfig: Updated configuration after storing the checkpoint.
        """
        thread_id = config["configurable"]["thread_id"] # type: ignore
        checkpoint_ns = config["configurable"]["checkpoint_ns"] # type: ignore
        checkpoint_id = checkpoint["id"]
        parent_checkpoint_id = config["configurable"].get("checkpoint_id")  # type: ignore
        key = _make_redis_checkpoint_key(thread_id, checkpoint_ns, checkpoint_id)

        type_, serialized_checkpoint = self.serde.dumps_typed(checkpoint)
        serialized_metadata = self.serde.dumps(metadata)
        data = {
            "checkpoint": serialized_checkpoint,
            "type": type_,
            "metadata": serialized_metadata,
            "parent_checkpoint_id": parent_checkpoint_id
            if parent_checkpoint_id
            else "",
        }
        self.conn.hset(key, mapping=data)
        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
            }
        }

    def put_writes( # type: ignore
        self,
        config: RunnableConfig,
        writes: List[Tuple[str, Any]],
        task_id: str,
    ) -> None:
        """Store intermediate writes linked to a checkpoint.

        Args:
            config (RunnableConfig): Configuration of the related checkpoint.
            writes (Sequence[Tuple[str, Any]]): List of writes to store, each as (channel, value) pair.
            task_id (str): Identifier for the task creating the writes.
        """
        thread_id = config["configurable"]["thread_id"] # type: ignore
        checkpoint_ns = config["configurable"]["checkpoint_ns"] # type: ignore
        checkpoint_id = config["configurable"]["checkpoint_id"] # type: ignore

        for idx, (channel, value) in enumerate(writes):
            key = _make_redis_checkpoint_writes_key(
                thread_id,
                checkpoint_ns,
                checkpoint_id,
                task_id,
                WRITES_IDX_MAP.get(channel, idx),
            )
            type_, serialized_value = self.serde.dumps_typed(value)
            data = {"channel": channel, "type": type_, "value": serialized_value}
            if all(w[0] in WRITES_IDX_MAP for w in writes):
                # Use HSET which will overwrite existing values
                self.conn.hset(key, mapping=data)
            else:
                # Use HSETNX which will not overwrite existing values
                for field, value in data.items():
                    self.conn.hsetnx(key, field, value)

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """Get a checkpoint tuple from Redis.

        This method retrieves a checkpoint tuple from Redis based on the
        provided config. If the config contains a "checkpoint_id" key, the checkpoint with
        the matching thread ID and checkpoint ID is retrieved. Otherwise, the latest checkpoint
        for the given thread ID is retrieved.

        Args:
            config (RunnableConfig): The config to use for retrieving the checkpoint.

        Returns:
            Optional[CheckpointTuple]: The retrieved checkpoint tuple, or None if no matching checkpoint was found.
        """
        thread_id = config["configurable"]["thread_id"] # type: ignore
        checkpoint_id = get_checkpoint_id(config)
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "") # type: ignore

        checkpoint_key = self._get_checkpoint_key(
            self.conn, thread_id, checkpoint_ns, checkpoint_id
        )
        if not checkpoint_key:
            return None

        checkpoint_data = self.conn.hgetall(checkpoint_key)

        # load pending writes
        checkpoint_id = (
            checkpoint_id
            or _parse_redis_checkpoint_key(checkpoint_key)["checkpoint_id"]
        )
        pending_writes = self._load_pending_writes(
            thread_id, checkpoint_ns, checkpoint_id
        )
        return _parse_redis_checkpoint_data(
            self.serde, checkpoint_key, checkpoint_data, pending_writes=pending_writes # type: ignore
        )

    def list(
        self,
        config: Optional[RunnableConfig],
        *,
        # TODO: implement filtering
        filter: Optional[dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> Iterator[CheckpointTuple]:
        """List checkpoints from the database.

        This method retrieves a list of checkpoint tuples from Redis based
        on the provided config. The checkpoints are ordered by checkpoint ID in descending order (newest first).

        Args:
            config (RunnableConfig): The config to use for listing the checkpoints.
            filter (Optional[Dict[str, Any]]): Additional filtering criteria for metadata. Defaults to None.
            before (Optional[RunnableConfig]): If provided, only checkpoints before the specified checkpoint ID are returned. Defaults to None.
            limit (Optional[int]): The maximum number of checkpoints to return. Defaults to None.

        Yields:
            Iterator[CheckpointTuple]: An iterator of checkpoint tuples.
        """
        thread_id = config["configurable"]["thread_id"] # type: ignore
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "") # type: ignore
        pattern = _make_redis_checkpoint_key(thread_id, checkpoint_ns, "*")

        keys = _filter_keys(self.conn.keys(pattern), before, limit) # type: ignore
        for key in keys:
            data = self.conn.hgetall(key)
            if data and b"checkpoint" in data and b"metadata" in data: # type: ignore
                # load pending writes
                checkpoint_id = _parse_redis_checkpoint_key(key.decode())[
                    "checkpoint_id"
                ]
                pending_writes = self._load_pending_writes(
                    thread_id, checkpoint_ns, checkpoint_id
                )
                yield _parse_redis_checkpoint_data(
                    self.serde, key.decode(), data, pending_writes=pending_writes # type: ignore
                )

    def _load_pending_writes(
        self, thread_id: str, checkpoint_ns: str, checkpoint_id: str
    ) -> List[PendingWrite]:
        writes_key = _make_redis_checkpoint_writes_key(
            thread_id, checkpoint_ns, checkpoint_id, "*", None
        )
        matching_keys = self.conn.keys(pattern=writes_key)
        parsed_keys = [
            _parse_redis_checkpoint_writes_key(key.decode()) for key in matching_keys # type: ignore
        ]
        pending_writes = _load_writes(
            self.serde,
            {
                (parsed_key["task_id"], parsed_key["idx"]): self.conn.hgetall(key)
                for key, parsed_key in sorted(
                    zip(matching_keys, parsed_keys), key=lambda x: x[1]["idx"] # type: ignore
                )
            },
        )
        return pending_writes

    def _get_checkpoint_key(
        self, conn, thread_id: str, checkpoint_ns: str, checkpoint_id: Optional[str]
    ) -> Optional[str]:
        """Determine the Redis key for a checkpoint."""
        if checkpoint_id:
            return _make_redis_checkpoint_key(thread_id, checkpoint_ns, checkpoint_id)

        all_keys = conn.keys(_make_redis_checkpoint_key(thread_id, checkpoint_ns, "*"))
        if not all_keys:
            return None

        latest_key = max(
            all_keys,
            key=lambda k: _parse_redis_checkpoint_key(k.decode())["checkpoint_id"],
        )
        return latest_key.decode()
    
    # Set up storage 
store = InMemoryStore(
    index={
        "dims": 1536,
        "embed": "openai:text-embedding-3-small",
    }
)