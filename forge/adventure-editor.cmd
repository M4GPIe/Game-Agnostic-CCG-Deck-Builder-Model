@echo off

pushd %~dp0

java -version 1>nul 2>nul || (
   echo no java installed
   popd
   exit /b 2
)
for /f tokens^=2^ delims^=.-_^+^" %%j in ('java -fullversion 2^>^&1') do set "jver=%%j"

if %jver% LEQ 16 (
   echo unsupported java
   popd
   exit /b 2
)

if %jver% GEQ 17 (
  java -Xmx4096m -Dfile.encoding=UTF-8 -jar adventure-editor-jar-with-dependencies.jar
  popd
  exit /b 0
)

popd