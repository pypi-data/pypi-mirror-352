"""
Project Settings Management

This module provides functionality for managing project settings and persistent data
for the Code Index MCP server.
"""
import os
import json
import shutil
import pickle
import tempfile
import hashlib
from datetime import datetime

class ProjectSettings:
    """Class for managing project settings and index data"""

    SETTINGS_DIR = "code_indexer"
    CONFIG_FILE = "config.json"
    INDEX_FILE = "file_index.pickle"
    CACHE_FILE = "content_cache.pickle"

    def __init__(self, base_path, skip_load=False):
        """Initialize project settings

        Args:
            base_path (str): Base path of the project
            skip_load (bool): Whether to skip loading files
        """
        self.base_path = base_path
        self.skip_load = skip_load

        # Ensure the base path of the temporary directory exists
        try:
            # Get system temporary directory
            system_temp = tempfile.gettempdir()
            print(f"System temporary directory: {system_temp}")

            # Check if the system temporary directory exists and is writable
            if not os.path.exists(system_temp):
                print(f"Warning: System temporary directory does not exist: {system_temp}")
                # Try using current directory as fallback
                system_temp = os.getcwd()
                print(f"Using current directory as fallback: {system_temp}")

            if not os.access(system_temp, os.W_OK):
                print(f"Warning: No write access to system temporary directory: {system_temp}")
                # Try using current directory as fallback
                system_temp = os.getcwd()
                print(f"Using current directory as fallback: {system_temp}")

            # Create code_indexer directory
            temp_base_dir = os.path.join(system_temp, self.SETTINGS_DIR)
            print(f"Code indexer directory path: {temp_base_dir}")

            if not os.path.exists(temp_base_dir):
                print(f"Creating code indexer directory: {temp_base_dir}")
                os.makedirs(temp_base_dir, exist_ok=True)

                # Create a README.md file explaining the purpose of this directory
                readme_path = os.path.join(temp_base_dir, "README.md")
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write("# Code Indexer Cache Directory\n\nThis directory contains cached data for the Code Index MCP tool.\nEach subdirectory corresponds to a different project.\n")
                print(f"README file created: {readme_path}")
            else:
                print(f"Code indexer directory already exists: {temp_base_dir}")
        except Exception as e:
            print(f"Error setting up temporary directory: {e}")
            # If unable to create temporary directory, use .code_indexer in current directory
            temp_base_dir = os.path.join(os.getcwd(), ".code_indexer")
            print(f"Using fallback directory: {temp_base_dir}")
            if not os.path.exists(temp_base_dir):
                os.makedirs(temp_base_dir, exist_ok=True)

        # Use system temporary directory to store index data
        try:
            if base_path:
                # Use hash of project path as unique identifier
                path_hash = hashlib.md5(base_path.encode()).hexdigest()
                self.settings_path = os.path.join(temp_base_dir, path_hash)
                print(f"Using project-specific directory: {self.settings_path}")
            else:
                # If no base path provided, use a default directory
                self.settings_path = os.path.join(temp_base_dir, "default")
                print(f"Using default directory: {self.settings_path}")

            self.ensure_settings_dir()
        except Exception as e:
            print(f"Error setting up project settings: {e}")
            # If error occurs, use .code_indexer in current directory as fallback
            fallback_dir = os.path.join(os.getcwd(), ".code_indexer",
                                      "default" if not base_path else hashlib.md5(base_path.encode()).hexdigest())
            print(f"Using fallback directory: {fallback_dir}")
            self.settings_path = fallback_dir
            if not os.path.exists(fallback_dir):
                os.makedirs(fallback_dir, exist_ok=True)

    def ensure_settings_dir(self):
        """Ensure settings directory exists"""
        print(f"Checking project settings directory: {self.settings_path}")

        try:
            if not os.path.exists(self.settings_path):
                print(f"Creating project settings directory: {self.settings_path}")
                # Create directory structure
                os.makedirs(self.settings_path, exist_ok=True)

                # Create a README.md file explaining the purpose of this directory
                readme_path = os.path.join(self.settings_path, "README.md")
                readme_content = (
                    f"# Code Indexer Cache Directory for {self.base_path}\n\n"
                    f"This directory contains cached data for the Code Index MCP tool:\n\n"
                    f"- `config.json`: Project configuration\n"
                    f"- `file_index.pickle`: Index of project files\n"
                    f"- `content_cache.pickle`: Cached file contents\n\n"
                    f"These files are automatically generated and stored in the system temporary directory.\n"
                )

                try:
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(readme_content)
                    print(f"README file created: {readme_path}")
                except Exception as e:
                    print(f"Warning: Could not create README file: {e}")
            else:
                print(f"Project settings directory already exists: {self.settings_path}")

            # Check if directory is writable
            if not os.access(self.settings_path, os.W_OK):
                print(f"Warning: No write access to project settings directory: {self.settings_path}")
                # If directory is not writable, use .code_indexer in current directory as fallback
                fallback_dir = os.path.join(os.getcwd(), ".code_indexer",
                                          os.path.basename(self.settings_path))
                print(f"Using fallback directory: {fallback_dir}")
                self.settings_path = fallback_dir
                if not os.path.exists(fallback_dir):
                    os.makedirs(fallback_dir, exist_ok=True)
        except Exception as e:
            print(f"Error ensuring settings directory: {e}")
            # If unable to create settings directory, use .code_indexer in current directory
            fallback_dir = os.path.join(os.getcwd(), ".code_indexer",
                                      "default" if not self.base_path else hashlib.md5(self.base_path.encode()).hexdigest())
            print(f"Using fallback directory: {fallback_dir}")
            self.settings_path = fallback_dir
            if not os.path.exists(fallback_dir):
                os.makedirs(fallback_dir, exist_ok=True)

    def get_config_path(self):
        """Get the path to the configuration file"""
        try:
            path = os.path.join(self.settings_path, self.CONFIG_FILE)
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            return path
        except Exception as e:
            print(f"Error getting config path: {e}")
            # If error occurs, use file in current directory as fallback
            return os.path.join(os.getcwd(), self.CONFIG_FILE)

    def get_index_path(self):
        """Get the path to the index file"""
        try:
            path = os.path.join(self.settings_path, self.INDEX_FILE)
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            return path
        except Exception as e:
            print(f"Error getting index path: {e}")
            # If error occurs, use file in current directory as fallback
            return os.path.join(os.getcwd(), self.INDEX_FILE)

    def get_cache_path(self):
        """Get the path to the cache file"""
        try:
            path = os.path.join(self.settings_path, self.CACHE_FILE)
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            return path
        except Exception as e:
            print(f"Error getting cache path: {e}")
            # If error occurs, use file in current directory as fallback
            return os.path.join(os.getcwd(), self.CACHE_FILE)

    def _get_timestamp(self):
        """Get current timestamp"""
        return datetime.now().isoformat()

    def save_config(self, config):
        """Save configuration data

        Args:
            config (dict): Configuration data
        """
        try:
            config_path = self.get_config_path()
            # Add timestamp
            config['last_updated'] = self._get_timestamp()

            # Ensure directory exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print(f"Config saved to: {config_path}")
            return config
        except Exception as e:
            print(f"Error saving config: {e}")
            return config

    def load_config(self):
        """Load configuration data

        Returns:
            dict: Configuration data, or empty dict if file doesn't exist
        """
        # If skip_load is set, return empty dict directly
        if self.skip_load:
            return {}

        try:
            config_path = self.get_config_path()
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    print(f"Config loaded from: {config_path}")
                    return config
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    print(f"Error parsing config file: {e}")
                    # If file is corrupted, return empty dict
                    return {}
            else:
                print(f"Config file does not exist: {config_path}")
            return {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def save_index(self, file_index):
        """Save file index

        Args:
            file_index (dict): File index data
        """
        try:
            index_path = self.get_index_path()
            print(f"Saving index to: {index_path}")

            # Ensure directory exists
            dir_path = os.path.dirname(index_path)
            if not os.path.exists(dir_path):
                print(f"Creating directory: {dir_path}")
                os.makedirs(dir_path, exist_ok=True)

            # Check if directory is writable
            if not os.access(dir_path, os.W_OK):
                print(f"Warning: Directory is not writable: {dir_path}")
                # Use current directory as fallback
                index_path = os.path.join(os.getcwd(), self.INDEX_FILE)
                print(f"Using fallback path: {index_path}")

            with open(index_path, 'wb') as f:
                pickle.dump(file_index, f)

            print(f"Index saved successfully to: {index_path}")
        except Exception as e:
            print(f"Error saving index: {e}")
            # Try saving to current directory
            try:
                fallback_path = os.path.join(os.getcwd(), self.INDEX_FILE)
                print(f"Trying fallback path: {fallback_path}")
                with open(fallback_path, 'wb') as f:
                    pickle.dump(file_index, f)
                print(f"Index saved to fallback path: {fallback_path}")
            except Exception as e2:
                print(f"Error saving index to fallback path: {e2}")

    def load_index(self):
        """Load file index

        Returns:
            dict: File index data, or empty dict if file doesn't exist
        """
        # If skip_load is set, return empty dict directly
        if self.skip_load:
            return {}

        try:
            index_path = self.get_index_path()

            if os.path.exists(index_path):
                try:
                    with open(index_path, 'rb') as f:
                        index = pickle.load(f)
                    print(f"Index loaded successfully from: {index_path}")
                    return index
                except (pickle.PickleError, EOFError) as e:
                    print(f"Error parsing index file: {e}")
                    # If file is corrupted, return empty dict
                    return {}
                except Exception as e:
                    print(f"Unexpected error loading index: {e}")
                    return {}
            else:
                # Try loading from current directory
                fallback_path = os.path.join(os.getcwd(), self.INDEX_FILE)
                if os.path.exists(fallback_path):
                    print(f"Trying fallback path: {fallback_path}")
                    try:
                        with open(fallback_path, 'rb') as f:
                            index = pickle.load(f)
                        print(f"Index loaded from fallback path: {fallback_path}")
                        return index
                    except Exception as e:
                        print(f"Error loading index from fallback path: {e}")

            return {}
        except Exception as e:
            print(f"Error in load_index: {e}")
            return {}

    def save_cache(self, content_cache):
        """Save content cache

        Args:
            content_cache (dict): Content cache data
        """
        try:
            cache_path = self.get_cache_path()
            print(f"Saving cache to: {cache_path}")

            # Ensure directory exists
            dir_path = os.path.dirname(cache_path)
            if not os.path.exists(dir_path):
                print(f"Creating directory: {dir_path}")
                os.makedirs(dir_path, exist_ok=True)

            # Check if directory is writable
            if not os.access(dir_path, os.W_OK):
                print(f"Warning: Directory is not writable: {dir_path}")
                # Use current directory as fallback
                cache_path = os.path.join(os.getcwd(), self.CACHE_FILE)
                print(f"Using fallback path: {cache_path}")

            with open(cache_path, 'wb') as f:
                pickle.dump(content_cache, f)

            print(f"Cache saved successfully to: {cache_path}")
        except Exception as e:
            print(f"Error saving cache: {e}")
            # Try saving to current directory
            try:
                fallback_path = os.path.join(os.getcwd(), self.CACHE_FILE)
                print(f"Trying fallback path: {fallback_path}")
                with open(fallback_path, 'wb') as f:
                    pickle.dump(content_cache, f)
                print(f"Cache saved to fallback path: {fallback_path}")
            except Exception as e2:
                print(f"Error saving cache to fallback path: {e2}")

    def load_cache(self):
        """Load content cache

        Returns:
            dict: Content cache data, or empty dict if file doesn't exist
        """
        # If skip_load is set, return empty dict directly
        if self.skip_load:
            return {}

        try:
            cache_path = self.get_cache_path()

            if os.path.exists(cache_path):
                try:
                    with open(cache_path, 'rb') as f:
                        cache = pickle.load(f)
                    print(f"Cache loaded successfully from: {cache_path}")
                    return cache
                except (pickle.PickleError, EOFError) as e:
                    print(f"Error parsing cache file: {e}")
                    # If file is corrupted, return empty dict
                    return {}
                except Exception as e:
                    print(f"Unexpected error loading cache: {e}")
                    return {}
            else:
                # Try loading from current directory
                fallback_path = os.path.join(os.getcwd(), self.CACHE_FILE)
                if os.path.exists(fallback_path):
                    print(f"Trying fallback path: {fallback_path}")
                    try:
                        with open(fallback_path, 'rb') as f:
                            cache = pickle.load(f)
                        print(f"Cache loaded from fallback path: {fallback_path}")
                        return cache
                    except Exception as e:
                        print(f"Error loading cache from fallback path: {e}")

            return {}
        except Exception as e:
            print(f"Error in load_cache: {e}")
            return {}

    def clear(self):
        """Clear all settings and cache files"""
        try:
            print(f"Clearing settings directory: {self.settings_path}")

            if os.path.exists(self.settings_path):
                # Check if directory is writable
                if not os.access(self.settings_path, os.W_OK):
                    print(f"Warning: Directory is not writable: {self.settings_path}")
                    return

                # Preserve .gitignore file
                gitignore_path = os.path.join(self.settings_path, ".gitignore")
                has_gitignore = os.path.exists(gitignore_path)
                gitignore_content = None

                if has_gitignore:
                    try:
                        with open(gitignore_path, 'r', encoding='utf-8') as f:
                            gitignore_content = f.read()
                        print(f"Preserved .gitignore content")
                    except Exception as e:
                        print(f"Error reading .gitignore: {e}")

                # Delete all files in the directory
                try:
                    for filename in os.listdir(self.settings_path):
                        file_path = os.path.join(self.settings_path, filename)
                        try:
                            if os.path.isfile(file_path):
                                os.unlink(file_path)
                                print(f"Deleted file: {file_path}")
                            elif os.path.isdir(file_path):
                                shutil.rmtree(file_path)
                                print(f"Deleted directory: {file_path}")
                        except Exception as e:
                            print(f"Error deleting {file_path}: {e}")
                except Exception as e:
                    print(f"Error listing directory: {e}")

                # Restore .gitignore file
                if has_gitignore and gitignore_content:
                    try:
                        with open(gitignore_path, 'w', encoding='utf-8') as f:
                            f.write(gitignore_content)
                        print(f"Restored .gitignore file")
                    except Exception as e:
                        print(f"Error restoring .gitignore: {e}")

                print(f"Settings directory cleared successfully")
            else:
                print(f"Settings directory does not exist: {self.settings_path}")
        except Exception as e:
            print(f"Error clearing settings: {e}")

    def get_stats(self):
        """Get statistics for the settings directory

        Returns:
            dict: Dictionary containing file sizes and update times
        """
        try:
            print(f"Getting stats for settings directory: {self.settings_path}")

            stats = {
                'settings_path': self.settings_path,
                'exists': os.path.exists(self.settings_path),
                'is_directory': os.path.isdir(self.settings_path) if os.path.exists(self.settings_path) else False,
                'writable': os.access(self.settings_path, os.W_OK) if os.path.exists(self.settings_path) else False,
                'files': {},
                'temp_dir': tempfile.gettempdir(),
                'current_dir': os.getcwd()
            }

            if stats['exists'] and stats['is_directory']:
                try:
                    # Get all files in the directory
                    all_files = os.listdir(self.settings_path)
                    stats['all_files'] = all_files

                    # Get details for specific files
                    for filename in [self.CONFIG_FILE, self.INDEX_FILE, self.CACHE_FILE]:
                        file_path = os.path.join(self.settings_path, filename)
                        if os.path.exists(file_path):
                            try:
                                file_stats = os.stat(file_path)
                                stats['files'][filename] = {
                                    'path': file_path,
                                    'size_bytes': file_stats.st_size,
                                    'last_modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                                    'readable': os.access(file_path, os.R_OK),
                                    'writable': os.access(file_path, os.W_OK)
                                }
                            except Exception as e:
                                stats['files'][filename] = {
                                    'path': file_path,
                                    'error': str(e)
                                }
                except Exception as e:
                    stats['list_error'] = str(e)

            # Check fallback path
            fallback_dir = os.path.join(os.getcwd(), ".code_indexer")
            stats['fallback_path'] = fallback_dir
            stats['fallback_exists'] = os.path.exists(fallback_dir)
            stats['fallback_is_directory'] = os.path.isdir(fallback_dir) if os.path.exists(fallback_dir) else False

            return stats
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {
                'error': str(e),
                'settings_path': self.settings_path,
                'temp_dir': tempfile.gettempdir(),
                'current_dir': os.getcwd()
            }
