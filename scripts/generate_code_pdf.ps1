$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$outputPath = Join-Path $projectRoot "thesis_code_listing.pdf"

$includeFiles = @(
    ".gitignore",
    "README.md",
    "requirements.txt",
    "app.py",
    "src\breed_recognition.py",
    "scripts\build_index.py",
    "android_app\pubspec.yaml",
    "android_app\analysis_options.yaml"
)

function Escape-PdfText {
    param([string]$Text)
    $escaped = $Text.Replace('\', '\\')
    $escaped = $escaped.Replace('(', '\(')
    $escaped = $escaped.Replace(')', '\)')
    return $escaped
}

function Add-Line {
    param(
        [System.Collections.Generic.List[string]]$Pages,
        [ref]$Current,
        [ref]$LineCount,
        [string]$Text
    )

    if ($LineCount.Value -ge 48) {
        $Pages.Add($Current.Value)
        $Current.Value = ""
        $LineCount.Value = 0
    }

    $safeText = Escape-PdfText $Text
    $Current.Value += "BT /F1 9 Tf 40 " + (790 - ($LineCount.Value * 15)) + " Td (" + $safeText + ") Tj ET`n"
    $LineCount.Value++
}

$pages = New-Object 'System.Collections.Generic.List[string]'
$currentPage = ""
$lineCount = 0

foreach ($relativePath in $includeFiles) {
    $filePath = Join-Path $projectRoot $relativePath
    if (-not (Test-Path $filePath)) {
        continue
    }

    Add-Line -Pages $pages -Current ([ref]$currentPage) -LineCount ([ref]$lineCount) -Text ("FILE: " + $relativePath)
    Add-Line -Pages $pages -Current ([ref]$currentPage) -LineCount ([ref]$lineCount) -Text ("")

    $lines = Get-Content $filePath
    $number = 1
    foreach ($line in $lines) {
        $prefix = "{0:D4}: " -f $number
        $chunks = @()
        if ($line.Length -le 95) {
            $chunks = @($line)
        } else {
            for ($i = 0; $i -lt $line.Length; $i += 95) {
                $length = [Math]::Min(95, $line.Length - $i)
                $chunks += $line.Substring($i, $length)
            }
        }

        for ($j = 0; $j -lt $chunks.Count; $j++) {
            $display = if ($j -eq 0) { $prefix + $chunks[$j] } else { "      " + $chunks[$j] }
            Add-Line -Pages $pages -Current ([ref]$currentPage) -LineCount ([ref]$lineCount) -Text $display
        }
        $number++
    }

    Add-Line -Pages $pages -Current ([ref]$currentPage) -LineCount ([ref]$lineCount) -Text ("")
    Add-Line -Pages $pages -Current ([ref]$currentPage) -LineCount ([ref]$lineCount) -Text ("")
}

if ($currentPage.Length -gt 0) {
    $pages.Add($currentPage)
}

$objects = New-Object System.Collections.ArrayList
[void]$objects.Add("1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj`n")

$kids = @()
$pageObjectIds = @()
$contentObjectIds = @()
$nextId = 3

for ($i = 0; $i -lt $pages.Count; $i++) {
    $pageObjectIds += $nextId
    $contentObjectIds += ($nextId + 1)
    $kids += "$nextId 0 R"
    $nextId += 2
}

[void]$objects.Add("2 0 obj << /Type /Pages /Count " + $pages.Count + " /Kids [ " + ($kids -join " ") + " ] >> endobj`n")

for ($i = 0; $i -lt $pages.Count; $i++) {
    $contentBytes = [System.Text.Encoding]::ASCII.GetBytes($pages[$i])
    $contentLength = $contentBytes.Length
    $pageId = $pageObjectIds[$i]
    $contentId = $contentObjectIds[$i]
    [void]$objects.Add("$pageId 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Courier >> >> >> /Contents $contentId 0 R >> endobj`n")
    [void]$objects.Add("$contentId 0 obj << /Length $contentLength >> stream`n" + $pages[$i] + "endstream`nendobj`n")
}

$pdf = "%PDF-1.4`n"
$offsets = New-Object System.Collections.Generic.List[int]
$offsets.Add(0) | Out-Null

foreach ($obj in $objects) {
    $offsets.Add([System.Text.Encoding]::ASCII.GetByteCount($pdf)) | Out-Null
    $pdf += $obj
}

$xrefStart = [System.Text.Encoding]::ASCII.GetByteCount($pdf)
$pdf += "xref`n0 " + ($objects.Count + 1) + "`n"
$pdf += "0000000000 65535 f `n"

for ($i = 1; $i -le $objects.Count; $i++) {
    $pdf += ("{0:D10} 00000 n `n" -f $offsets[$i])
}

$pdf += "trailer << /Size " + ($objects.Count + 1) + " /Root 1 0 R >>`n"
$pdf += "startxref`n$xrefStart`n%%EOF"

[System.IO.File]::WriteAllBytes($outputPath, [System.Text.Encoding]::ASCII.GetBytes($pdf))
Write-Output "Generated PDF: $outputPath"
