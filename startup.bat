:loop
taskkill /F /IM python.exe
taskkill /F /IM ffmpeg.exe

for /f %%i in ('powershell ^(get-date^).DayOfWeek') do set dow=%%i
if /i %time:~0,2% == 23 (if %dow% == Sunday (goto:test))

set /p g=< vgeigercom.txt

ping 127.0.0.1 -n 5
start c:\farlabs\stream.bat
start c:\farlabs\python\python.exe turntable.py geiger=%g%

:innerloop
timeout /t 60 /nobreak

time /t > tmpFile 
set /p timenow= < tmpFile 
del tmpFile 

echo /i %timenow:~3,2%
if /i %timenow:~3,2% == 00 (goto :loop)

goto :innerloop

:test
echo Start Automated Testing... 
timeout /t 5
cd C:\farlabs\weekly_expt_test\ 
start C:\farlabs\weekly_expt_test\turntables_testing.bat

exit


