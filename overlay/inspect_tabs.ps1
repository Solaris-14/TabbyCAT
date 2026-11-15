# UIAutomation Tab & URL Inspector for TabbyPatrol
param([int]$Hwnd)

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

if ($Hwnd -eq 0) {
    Write-Output '{"url":"","tabs":[]}'
    exit
}

try {
    $elem = [System.Windows.Automation.AutomationElement]::FromHandle([IntPtr]$Hwnd)
    if (-not $elem) {
        Write-Output '{"url":"","tabs":[]}'
        exit
    }

    $winRect = $elem.Current.BoundingRectangle
    $winTop = [int]$winRect.Top

    # 1. Address bar URL extraction
    $url = ""
    try {
        $nameCond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, "Address and search bar")
        $addrElem = $elem.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $nameCond)
        if (-not $addrElem) {
            $nameCond2 = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, "Address bar")
            $addrElem = $elem.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $nameCond2)
        }
        if ($addrElem) {
            $valPat = $null
            try { $valPat = $addrElem.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern) } catch {}
            if ($valPat -ne $null -and $valPat.Current.Value) {
                $url = [string]$valPat.Current.Value
            }
        }
    } catch {}

    # 2. Tab items extraction
    $tabCond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::TabItem)
    $tabs = $elem.FindAll([System.Windows.Automation.TreeScope]::Descendants, $tabCond)

    $list = @()
    foreach ($t in $tabs) {
        $rect = $t.Current.BoundingRectangle
        $tTop = [int]$rect.Top
        $tHeight = [int]$rect.Height

        # Browser tabs are at the top of the browser window
        if ($winTop -gt 0 -and $tTop -ge ($winTop + 140)) {
            continue
        }

        $sel = $null
        try {
            $sel = $t.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern)
        } catch {}

        $isSelected = ($sel -ne $null -and $sel.Current.IsSelected)

        $list += @{
            name = $t.Current.Name
            selected = $isSelected
            left = [int]$rect.Left
            top = [int]$rect.Top
            right = [int]$rect.Right
            bottom = [int]$rect.Bottom
            width = [int]$rect.Width
            height = [int]$rect.Height
        }
    }

    $res = @{
        url = $url
        tabs = @($list)
    }
    $json = ConvertTo-Json -InputObject $res -Compress
    Write-Output $json
} catch {
    Write-Output '{"url":"","tabs":[]}'
}
