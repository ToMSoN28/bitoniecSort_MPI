# Definicja komend do wykonania
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

# Tablica do przechowywania wyników
$results = @()

foreach ($command in $commands) {
    # Mierzenie czasu wykonania komendy
    $executionTime = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        Invoke-Expression $command
    } catch {
        Write-Host "Error executing $($command): $($_.Exception.Message)"
    }
    $executionTime.Stop()

    # Zapisanie wyniku
    $results += [pscustomobject]@{
        Command = $command
        TimeInMilliseconds = $executionTime.Elapsed.TotalMilliseconds
    }
}

# Wyświetlenie wyników
$results | Format-Table -AutoSize
