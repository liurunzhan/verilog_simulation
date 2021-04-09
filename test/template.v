
// used to test connections between modules

`define PRINT_ERR_COUNT 10
// source signal delay time
`define DELAY1 0
// source signal delay time
`define DELAY2 0
// enable win width ignore
`define DELAY3 2
// check width ignore
`define DELAY4 1
// start check time
`define DELAY5 500

int index   = $subcaseNo;
bit source1 = 0;
bit source2 = 0;
bit source3 = 0;
bit enable1 = 0;
bit enable2 = 0;
bit enable3 = 0;

always #(6)      source1 = !source1;
always #(7)      source2 = !source2;
always #(10)     source3 = !source3;
always #(50001)  enable1 = !enable1;
always #(100001) enable2 = !enable2;
always #(150001) enable3 = !enable3;

initial begin
  #1ms;
  $finish;
end

///////////
///////////

wire enable_0;
assign enable_0 = 1;
`define SOURCE_SIGNAL_0   `TIM5_DIR.tim_trgo
`define SOURCE_SIGNAL_0_0 `TIM5_DIR.tim_trgo
`define SOURCE_NUMBER_0   1
`define DEST_SIGNAL_0     `TIM1_DIR.tim_itr0

always @(*) begin
  if (enable_$subcaseNo) begin
    force `SOURCE_SIGNAL_$subcaseNo_$i = source1;
  end else begin
    release `SOURCE_SIGNAL_$subcaseNo_$i;
  end
end

///////////
///////////

wire [`SOURCE_NUMBER_$subcaseNo-1:0] source_delay;
wire enable_delay;

assign #`DELAY1 source_delay = `SOURCE_SIGNAL_$subcaseNo;
assign #`DELAY3 enable_delay = enable_$subcaseNo;

wire check_result;
assign check_result = (`DEST_SIGNAL_$subcaseNo !== source_delay) & enable_$subcaseNo & enable_delay;

integer error_count = 0;
initial begin
#`DELAY5;
  forever begin
    @(posedge check_result);
	#`DELAY4;
	if(check_result) begin
	  error_count = error_count + 1;
	  if(error_count <= `PRINT_ERR_COUNT) begin
	    $display("ERROR: %t,signal connection check failed", $realtime);
	  end
	end
  end
end