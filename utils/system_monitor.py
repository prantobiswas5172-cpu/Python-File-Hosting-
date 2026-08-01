import psutil

def get_system_stats() -> str:
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return (f"🖥 **System Status**\n\n"
            f"**CPU:** {cpu}%\n"
            f"**RAM:** {ram.percent}% ({ram.used//1048576}MB / {ram.total//1048576}MB)\n"
            f"**Storage:** {disk.percent}% ({disk.used//1073741824}GB / {disk.total//1073741824}GB)")