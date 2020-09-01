$m = "ECM v3"
$b = "ECM v2"

get-childitem -Path "C:\Trigger-AI\examples\2D_points_results" | 
where-object { $_.Name -match $m } | 
ForEach-Object { rename-item $_.FullName -newname ($_.Name -replace $m, $b) }