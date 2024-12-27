###======# Still under developing ###

from fsm.assign import Equations
import textwrap

def genModule(dir: str, filename: str, moduleName: str, eqs: Equations, testSequence: str, tbsuffix: str = "tb"):
	istr = ",\n".join(map(lambda s: f"input {s}", eqs.inputs))
	ostr = ",\n".join(map(lambda s: f"output {s}", eqs.outputs))
	wire1 = ", ".join(map(lambda tp: f"D{str(tp[0])[:-1]}", eqs.nxtEqs.items()))
	wire2 = ", ".join(map(lambda tp: f"{str(tp[0])[:-1]}", eqs.nxtEqs.items()))
	nxteqstr = "\n".join(map(lambda tp: f"assign D{str(tp[0])[:-1]} = {tp[1]};", eqs.nxtEqs.items()))
	outeqstr = "\n".join(map(lambda tp: f"assign {str(tp[0])} = {tp[1]};", eqs.outEqs.items()))
	dffs = "\n".join(map(lambda tp: f"DFF DFF_{str(tp[0])[:-1]}(clk, D{str(tp[0])[:-1]}, {str(tp[0])[:-1]});", eqs.nxtEqs.items()))
	with open(f"{dir}/{filename}", mode="w", encoding="utf-8") as file:
		file.write(textwrap.dedent(f"""\
module {moduleName}(
	input clk,
	{istr},
	{ostr}
);
wire {wire1};
wire {wire2};

{nxteqstr}

{dffs}

{outeqstr}

endmodule

module DFF(
	input clk,
	input D,
	output reg Q
);
always @(posedge clk) 
begin
	Q <= D; 
end
endmodule
"""))
	
	ireg = ", ".join(map(str, eqs.inputs))
	owire = ", ".join(map(str, eqs.outputs))
	itbstr = ", ".join(map(lambda s: f".{s}({s})", eqs.inputs))
	otbstr = ", ".join(map(lambda s: f".{s}({s})", eqs.outputs))

	if len(eqs.inputs) == 1:
		teststr = "".join(map(lambda c: f"\t{eqs.inputs[0]} = 1'b{int(c)};\n\t#10;\n", testSequence))
	
	with open(f"{dir}/{filename.removesuffix(".v")}_{tbsuffix}.v", mode="w", encoding="utf-8") as file:
		file.write(textwrap.dedent(f"""\
`timescale 1ns/1ps
`define CYCLE_TIME 10.0
`include "{filename}"

module {moduleName}_{tbsuffix};

reg clk;
reg {ireg};
wire {owire};

real CYCLE = `CYCLE_TIME;
always #(CYCLE/2.0) clk = ~clk;
initial clk = 0;

{moduleName} U0(.clk(clk), {itbstr}, {otbstr});

initial
begin
{teststr}
	$finish;
end

initial
begin
	$dumpfile("wave.vcd");
	$dumpvars(0, {moduleName}_{tbsuffix});
end

endmodule
"""))