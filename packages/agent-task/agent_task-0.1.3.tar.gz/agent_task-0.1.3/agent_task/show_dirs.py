from appdirs import AppDirs

# Initialize with app and company name
dirs = AppDirs(appname="agent-task", appauthor="microwiseai")

# Print all directory locations
print("Application Directories:")
print(f"User Data Dir:  {dirs.user_data_dir}")
print(f"User Config:    {dirs.user_config_dir}")
print(f"User Cache:     {dirs.user_cache_dir}")
print(f"User Log:       {dirs.user_log_dir}")
print(f"\nSite-wide Directories:")
print(f"Site Data Dir:  {dirs.site_data_dir}")
print(f"Site Config:    {dirs.site_config_dir}") 

