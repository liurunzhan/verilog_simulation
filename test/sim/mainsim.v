`timescale 1ns/1ns

module top();
	
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

test u_test (
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
    $dumpfile("mainsim.vcd");
    $dumpvars;
    #TIME_FINISH $finish;
  end
endmodule

