Add-Type -AssemblyName 'System.IO.Compression.FileSystem'
$zip = [System.IO.Compression.ZipFile]::OpenRead('c:\Users\kaane\OneDrive\Desktop\bitirme-main\ADU-MF-ThesisTemplate-2018-07-19.docx')
$entry = $zip.Entries | Where-Object { $_.FullName -eq 'word/document.xml' }
$stream = $entry.Open()
$reader = New-Object System.IO.StreamReader($stream)
$content = $reader.ReadToEnd()
$reader.Close()
$stream.Close()
$zip.Dispose()

# Strip XML tags to get plain text
$plainText = $content -replace '<[^>]+>', ' '
$plainText = $plainText -replace '\s+', ' '
$plainText | Out-File -FilePath 'c:\Users\kaane\OneDrive\Desktop\bitirme-main\template_plain.txt' -Encoding UTF8

# Also save raw XML
$content | Out-File -FilePath 'c:\Users\kaane\OneDrive\Desktop\bitirme-main\template_raw.xml' -Encoding UTF8

Write-Host "Done! Files saved."
