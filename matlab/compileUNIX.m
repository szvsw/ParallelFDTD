clear mex
fprintf('Compiling  mex_FDTD\n');

% Specify linker flags for different libraries
cudaLibraries =  '-lcudart -lcuda ';
%glutAndGLlibraries = '-lglut -lGLU -lGL ';
%glewLibrary = '-l"/usr/lib/x86_64-linux-gnu/libGLEW.so" ';
boostLibraries = '-lboost_thread-mt -lboost_system-mt -lboost_date_time-mt ';
mexSpesificLibraries = '-lmx -lut ';
FDTDlibraries = '-llibParallelFDTD -lVoxelizer';

% Whole link command
link_flags = [cudaLibraries, ...
              boostLibraries, ...
              mexSpesificLibraries, ...
              FDTDlibraries
              ];

compile_command = ['mex -L"' additionalLibPath '" ', ...
                  link_flags]

% Compile
eval([compile_command ' device_reset.cpp ']);
eval([compile_command ' mex_FDTD.cpp']);
eval([compile_command ' mem_check.cpp']);

fprintf('Compile done\n');
clear all
