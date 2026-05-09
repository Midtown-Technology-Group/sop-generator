param(
    [string]$HostName = "127.0.0.1",
    [int]$Port = 8765
)

python -m sop_generator init-style
python -m sop_generator serve --host $HostName --port $Port
