& jupyter nbconvert --to script *.ipynb

$header = @"
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"@
# ls *.py | % { $($header; (Get-Content $_)) | Set-Content $_}