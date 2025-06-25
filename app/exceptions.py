# app/exceptions.py
class InventoryException(Exception):
    """Base exception for all inventory operations"""
    status_code = 500

class HostNotFoundException(InventoryException):
    """Raised when a host is not found in inventory"""
    status_code = 404

class NoGroupsException(InventoryException):
    """Raised when a host doesn't belong to any groups"""
    status_code = 400

class InvalidGroupException(InventoryException):
    """Raised when a host doesn't belong to recognized groups"""
    status_code = 400

class HostAlreadyExistsException(InventoryException):
    """Raised when trying to add a host that already exists in inventory"""
    status_code = 409


class GitException(Exception):
    """Base exception for Git operations"""
    status_code = 500

class GitGetOrCloneException(GitException):
    """Raised when there is an error getting or cloning a Git repository"""
    status_code = 500

class GitInitException(GitException):
    """Raised when there is an error initializing a Git repository"""
    status_code = 500

class GitPullException(GitException):
    """Raised when there is an error pulling changes from a Git repository"""
    status_code = 500

class GitPushException(GitException):
    """Raised when there is an error pushing changes to a Git repository"""
    status_code = 500