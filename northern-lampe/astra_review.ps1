$ErrorActionPreference='Stop'
$prompt=@'
You are an expert design-for-manufacture mechanical and lighting engineer reviewing a new Northern table lamp. The visual reference is one perspective concept render, NOT engineering documentation. Description: a large smooth, slightly tilted matte charcoal elliptic disk canopy, approx 310 mm across, with a thin concealed continuous warm-white crescent slot along its lower/front underside and a smaller warm halo gap toward its upper/rear underside. The head hangs asymmetrically from the top of a slender tall rounded monolithic side pedestal. The pedestal turns into a small, low, rounded foot/base, creating a letter-J or hook in elevation. No exposed screws. The design is elegant/minimal; preserve this silhouette as much as possible. The display model must show separate mechanical, optical and electrical parts and a kinematically plausible pivot.
Existing brief has hard targets: low glare and screen reflections; seamless work-to-ambient dimming; <=3000K, CRI >=90; target 350 lux average on a 600x400 mm work plane; portable <=1.2 kg; stable base; serviceable battery in <=1 min and LED in <=5 min with common tools; 10 main components max preferred; body safe to handle ~40C; 7.5W input work lighting via cable and optional 4h battery-powered ambient mode; parts separable and replaceable. Prototype likely desktop 3D printed and laser cut sheets, production potentially die-cast aluminum and injection PC.
Proposed scale: head elliptical 320x255 mm, canopy 2mm Al, underside LED carrier and separate PC opal slit lens front, rear halo back, offset pedestal near left, 170x110 mm compact base with steel ballast, pivot at z=210-240 mm, head inclination ~32 degrees, pivot fastener M5, wired through stem.
Design challenge: mechanical feasibility of large head cantilever, pivot geometry/tilt stops/wire bend, thermal path, two lighting optical functions, stability under 10N horizontal accidental push, service access, minimal part count, visible seams, tolerances. Previous optics analyses found direct light and screen glare significant, so no unearned claims.
Return (in Norwegian Nynorsk) ONLY these concise sections:
1. Required geometric architecture with *specific dimensional starting values* and head-to-pivot relation, enough for parametric CadQuery.
2. How to engineer a strong but removable pedestal, hinge, head, battery, 5V/USB-C power, LED/diffuser path.
3. Quantitative checks: stability under 10N push, mass budget, rough illumination requirements, thermal dissipation, electrical current, clearance/wire bend. Identify impossible targets and assumptions.
4. Minimal assembly BOM including materials, fasteners, process, estimated mass and service sequence.
5. Ranked top 5 fatal risks and how to test them, emphasizing limits of CAD.
You are reviewing a prototype, not certifying a production object. Do not invent tested optical or compliance results. Explicitly flag infeasible features. Keep response under 1800 words.
'@
$req=@{model='gpt-6.2-astra';reasoning=@{effort='max'};input=@(@{role='user';content=@(@{type='input_text';text=$prompt})});max_output_tokens=8500;store=$true;background=$true}
$body=$req|ConvertTo-Json -Depth 12 -Compress
$response=Invoke-RestMethod -Method Post -Uri 'https://api.openai.com/v1/responses' -Headers @{Authorization=("Bearer "+$env:OPENAI_API_KEY)} -ContentType 'application/json; charset=utf-8' -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) -TimeoutSec 240
$output=($response.output | Where-Object {$_.type -eq 'message'} | ForEach-Object {$_.content | Where-Object {$_.type -eq 'output_text'} | ForEach-Object {$_.text}}) -join [Environment]::NewLine
$outpath=Join-Path $env:TEMP 'astra_northern_disc_review.txt'
[IO.File]::WriteAllText($outpath,$output,[Text.Encoding]::UTF8)
Write-Output ('model='+$response.model)
Write-Output ('response_status='+$response.status)
Write-Output ('output_chars='+$output.Length)
Write-Output ('usage_in='+$response.usage.input_tokens)
Write-Output ('usage_out='+$response.usage.output_tokens)
Write-Output ('file='+$outpath)
if($response.status -ne 'completed'){Write-Output ('incomplete='+($response.incomplete_details|ConvertTo-Json -Compress))}
