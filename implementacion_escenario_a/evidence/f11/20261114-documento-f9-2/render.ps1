$ErrorActionPreference = 'Stop'
$entrada = (Resolve-Path -LiteralPath 'output/doc/Arquitectura_C4_EIP_y_Funcionamiento_Arnes_F9_2.docx').Path
$carpeta = Join-Path (Get-Location).Path 'tmp/f9_2_documento'
$pdf = Join-Path $carpeta 'documento.pdf'
$word = $null
$documento = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $documento = $word.Documents.Open($entrada, $false, $true)
    $documento.Repaginate()
    $paginas = $documento.ComputeStatistics(2)
    $documento.ExportAsFixedFormat($pdf, 17)
    Write-Output ("Paginas renderizadas en Word: " + $paginas)
}
finally {
    if ($null -ne $documento) { $documento.Close(0) }
    if ($null -ne $word) { $word.Quit() }
}
