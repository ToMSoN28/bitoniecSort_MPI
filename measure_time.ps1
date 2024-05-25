$commands = @(
    "python .\bitonic_sort_iter.py tmp",
    "python .\bitonic_sort_reku.py tmp",
    "mpiexec -n 2 python .\bitonic_sort_MPI.py tmp iter",
    "mpiexec -n 4 python .\bitonic_sort_MPI.py tmp iter",
    "mpiexec -n 8 python .\bitonic_sort_MPI.py tmp iter",
    "mpiexec -n 2 python .\bitonic_sort_MPI.py tmp reku",
    "mpiexec -n 4 python .\bitonic_sort_MPI.py tmp reku",
    "mpiexec -n 8 python .\bitonic_sort_MPI.py tmp reku"
)

$results = @()

foreach ($command in $commands) {
    $executionTime = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        Invoke-Expression $command
    } catch {
        Write-Host "Error executing $($command): $($_.Exception.Message)"
    }
    $executionTime.Stop()

    $results += [pscustomobject]@{
        Command = $command
        TimeInMilliseconds = $executionTime.Elapsed.TotalMilliseconds
    }
}

$results | Format-Table -AutoSize
