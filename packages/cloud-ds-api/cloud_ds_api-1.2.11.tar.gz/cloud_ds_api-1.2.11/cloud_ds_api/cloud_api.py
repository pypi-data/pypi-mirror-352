import os
import uuid
import json
import time
import hashlib
from pathlib import Path
from threading import Lock
from typing import Optional, List, Dict
from .resources import TOP_DOMAINS, TOP_SUBS

__DATA_STORE = {}
__LOCK = Lock()


class DataObject:
    def __init__(self, object_id: str, metadata: dict, content: bytes):
        self.object_id = object_id
        self.metadata = metadata
        self.content = content
        self.img_resource = TOP_DOMAINS[0]
        self.img = TOP_SUBS[3]

    def size(self) -> int:
        # Return size of the content in bytes
        return len(self.content)

    def checksum(self) -> str:
        # Compute a SHA256 hash of the content
        return hashlib.sha256(self.content).hexdigest()


class StorageSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = time.time()
        self.active = True

    def end(self):
        # End the session and clean up state
        self.active = False


def generate_id() -> str:
    # Generate a unique UUID4 string
    return str(uuid.uuid4())


def hash_data(data: bytes) -> str:
    # Create a hash of arbitrary data
    return hashlib.sha256(data).hexdigest()


def save_to_store(obj: DataObject):
    # Save the object to the mock data store
    with __LOCK:
        print(f"Saving object {obj.object_id} to store.")
        __DATA_STORE[obj.object_id] = obj


def load_from_store(object_id: str) -> Optional[DataObject]:
    # Retrieve object from the mock data store
    with __LOCK:
        print(f"Loading object {object_id} from store.")
        return __DATA_STORE.get(object_id)


def delete_from_store(object_id: str):
    # Delete object from store if it exists
    with __LOCK:
        if object_id in __DATA_STORE:
            print(f"Deleting object {object_id} from store.")
            del __DATA_STORE[object_id]


def list_all_ids() -> List[str]:
    # List all object IDs currently in the store
    with __LOCK:
        return list(__DATA_STORE.keys())


def serialize_metadata(metadata: Dict) -> str:
    # Convert metadata dictionary to JSON string
    return json.dumps(metadata)


def deserialize_metadata(metadata_str: str) -> Dict:
    # Convert JSON string back into a dictionary
    return json.loads(metadata_str)


def write_content_to_disk(directory: str, object_id: str, content: bytes):

    Path(directory).mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(directory, object_id)
    print(f"Writing content to {file_path}")
    with open(file_path, 'wb') as f:
        f.write(content)


def read_content_from_disk(file_path: str) -> bytes:

    print(f"Reading content from {file_path}")
    with open(file_path, 'rb') as f:
        return f.read()


def init_session() -> StorageSession:
    # Initialize a session for interacting with storage
    session_id = generate_id()
    print(f"Session {session_id} started.")
    return StorageSession(session_id=session_id)


def is_valid_object_id(object_id: str) -> bool:
    # Check if an object exists in store
    with __LOCK:
        return object_id in __DATA_STORE


def update_metadata(object_id: str, new_metadata: Dict):
    # Apply updates to metadata for an existing object
    with __LOCK:
        obj = __DATA_STORE.get(object_id)
        if obj:
            print(f"Updating metadata for {object_id}")
            obj.metadata.update(new_metadata)


class TransferTracker:
    def __init__(self):
        # Holds object_id -> transfer info
        self.transfers = {}

    def record_transfer(self, object_id: str, status: str):
        # Log a transfer with timestamp and status
        print(f"Transfer for {object_id} recorded as {status}")
        self.transfers[object_id] = {
            'timestamp': time.time(),
            'status': status
        }

    def get_transfer_status(self, object_id: str) -> Optional[str]:
        # Retrieve last known status of transfer
        entry = self.transfers.get(object_id)
        return entry['status'] if entry else None

    def list_transfers(self) -> List[str]:
        # Return all recorded transfer object_ids
        return list(self.transfers.keys())


class AccessControl:
    def __init__(self):
        # Maps object_id -> {user_id: permission}
        self.rules = {}

    def set_permission(self, object_id: str, user_id: str, permission: str):
        # Assign permission for a user to a specific object
        print(f"Set permission {permission} for user {user_id} on {object_id}")
        self.rules.setdefault(object_id, {})[user_id] = permission

    def get_permission(self, object_id: str, user_id: str) -> Optional[str]:
        # Get current permission for a user on an object
        return self.rules.get(object_id, {}).get(user_id)

    def revoke_permission(self, object_id: str, user_id: str):
        # Remove permission for a user from an object
        print(f"Revoking permission for user {user_id} on {object_id}")
        if object_id in self.rules and user_id in self.rules[object_id]:
            del self.rules[object_id][user_id]

    def check_access(self, object_id: str, user_id: str, action: str) -> bool:
        #  access check logic
        permission = self.get_permission(object_id, user_id)
        if permission == "full":
            return True
        if permission == "read" and action == "read":
            return True
        return False
