set phone_number to "{phone_number}"
set message to "{message}"
set found to true

tell application "RingCentral for Mac"
    launch
    activate
end tell
tell application "System Events"
	tell application process "RingCentral Phone"
		tell window 1
            tell list 1
                tell checkbox 1
                    set {xPosition, yPosition} to position
                    set {xSize, ySize} to size
                    do shell script "cliclick c:" & xPosition + (xSize div 2) & "," & yPosition + (ySize div 2)
                    delay 0.1
                end tell
            end tell
			set value of text field 1 to phone_number
            delay 0.5
            tell static text 4
                set search_message to value
                if search_message does not contain text 1 thru 3 of phone_number 
                    set found to false
                end if
                if search_message does not contain text 4 thru 6 of phone_number 
                    set found to false
                end if
                if search_message does not contain text 7 thru 10 of phone_number 
                    set found to false
                end if
                if found is true
                    set {xPosition, yPosition} to position
                    set {xSize, ySize} to size
                    do shell script "cliclick c:" & xPosition + (xSize div 2) & "," & yPosition + (ySize div 2)
                end if
            end tell
            if found is false
                delay 0.5
                tell button "Compose text, (1 of 5)" to click
                delay 0.1
                set value of text field 1 of text field 2 to phone_number
                set value of text field "Type message field " to message
            else 
                delay 0.1
                set value of text field "Type message field " to message
            end if
            
        end tell
        
	end tell
end tell
