set /p fl_video_model=< vidmodel.txt
set /p fl_video_server=< vidserver.txt
set /p fl_video_port=< vidport.txt
c:\farlabs\python\python.exe streamer.py %fl_video_model% %fl_video_server% %fl_video_port%
exit