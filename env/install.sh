#!/bin/sh

# This is a script to install tools and manage simulation project

# go to tool directory
# clone repository of iverilog and install it
function install_iverilog() {
  tool_dir=$1
  
  if [ ! -d {tool_dir} ]; then
    mkdir -p ${tool_dir}
  fi
  
  if [ -z `which iverilog` ]; then
    cd ${tool_dir}
    git clone --recursive https://github.com/steveicarus/iverilog iverilog
    cd iverilog
    ./autoconf.sh
    ./configure
    make
    sudo make install
    cd ../..
  fi

  if [ -z `which iverilog` ]; then
    echo "verilog compiler is not installed or found!"
    exit 1
  fi

  return 0
}

# go to tool directory
# clone repository of gtkwave and install it
function isntall_gtkwave() {
  tool_dir=$1
  
  if [ ! -d {tool_dir} ]; then
    mkdir -p ${tool_dir}
  fi
  
  if [ -z `which gtkwave` ]; then
    cd ${tool_dir}
    git clone --recursive https://github.com/gtkwave/gtkwave gtkwave
    cd gtkwave/gtkwave3
    ./configure
    make
    sudo make install
    cd ../..
  fi

  if [ -z `which gtkwave` ]; then
    echo "wave debug software is not installed or found!"
    exit 1
  fi

  return 0
}

# go to tool directory
# clone repository of yosys and install it
function install_yosys() {
  tool_dir=$1
  
  if [ ! -d {tool_dir} ]; then
    mkdir -p ${tool_dir}
  fi

  if [ -z `which yosys` ]; then
    cd ${tool_dir}
    git clone --recursive https://github.com/YosysHQ/yosys yosys
    cd yosys
    make config-gcc
    make
    sudo make install
    cd ../..
  fi

  if [ -z `which yosys` ]; then
    echo "synthesis software is not installed or found!"
    exit 1
  fi

  return 0
}

function create_project() {
  root=$1
  sim_dir=${root}/sim
  src_dir=${root}/src
  
  if [ -z ${root} ]; then
    echo "project name cannot be empty!"
    exit 1
  fi

  if [ -d ${root} ]; then
    echo "project directory ${root} has alread existed!"
    echo "please remove or rename it or define a new project name"
    exit 1
  fi

  mkdir -p ${root}
  mkdir -p ${sim_dir}
  mkdir -p ${src_dir}
  # create Makefile in simulation directory
  echo ".PHONY: all clean
all:
	./run

clean:
	-rm -rf ../../${root}
" > ${sim_dir}/Makefile

  # create run in simulation directory to call iverilog and gtkwave
  echo "#!/bin/sh

rm -f mainsim mainsim.vcd mainsim.lxt
list=\`cat filelist\`
iverilog -s dut -g2012 -o mainsim mainsim.v \$list
vvp -n mainsim -lxt2
cp mainsim.vcd mainsim.lxt
gtkwave mainsim.lxt
" > ${sim_dir}/run

  # create file list in simulation directory
  echo  "../src/${root}.v" > ${sim_dir}/filelist

  # create ip top in source directory
  echo "module ${root} (
  rstn,
  clk
);
input rstn;
input clk;

endmodule
" > ${src_dir}/${root}.v

  # create top file in simulation directory
  echo "\`timescale 1ns/1ns

module dut();
	
reg sysrstn;
reg rstn;
reg clk;

parameter SYSRST_START  = 10;
parameter RST_START     = 20-SYSRST_START;
parameter CLK_START     = 30-RST_START;
parameter SYSRST_END    = 9900-SYSRST_START;
parameter TIME_FINISH   = 10000;
	
always @(*)
  begin
    if(!sysrstn)
        rstn = 1'b0;
    else
        rstn = #RST_START 1'b1;
  end
	
always @(*)
  begin
    if(!rstn)
        clk = 1'b0;
    else
        clk = #CLK_START ~clk;
  end

${root} u_${root} (
  .rstn (rst_n),
  .clk  (clk)
);
	
initial
  begin
    clk = 1'b0;
    sysrstn = 1'b0;
    #SYSRST_START sysrstn = 1'b1;
    #SYSRST_END sysrstn = 1'b0;
  end
	
initial
  begin
    \$dumpfile(\"mainsim.vcd\");
    \$dumpvars;
    #TIME_FINISH \$finish;
  end
endmodule
" > ${sim_dir}/mainsim.v
}

if [ $# -eq 0 ]; then
  echo "$0 help to get all supported command line arguments"
  exit 1
fi

case $1 in
"install")
  root=./tool
  echo "install TOOL $2 in DIRECTORY ${root}"
  case $2 in
    "iverilog")
  	install_iverilog ${root}
  	;;
    "gtkwave")
  	install_gtkwave ${root}
  	;;
    "yosys")
  	install_yosys ${root}
  	;;
    *)
  	install_iverilog ${root}
  	install_gtkwave ${root}
  	install_yosys ${root}
  	;;
  esac
  ;;
"create")
  echo "create PROJECT $2"
  create_project $2
  ;;
  "clean")
  echo "clean PROJECT $2"
  if [ -d $2 ]; then
    rm -rf $2
  fi
  ;;
"help")
  echo "$0 install iverilog/gtkwave/yosys"
  echo "$0 create project"
  echo "$0 clean project"
  echo "$0 help"
  ;;
*)
  echo "$0 help to get all supported command line arguments"
  ;;
esac
