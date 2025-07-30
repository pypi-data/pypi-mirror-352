// This file is public domain, it can be freely copied without restrictions.
// SPDX-License-Identifier: CC0-1.0
// Adder DUT
`timescale 1ns/1ps

module adder #(
  parameter integer DATA_WIDTH, TEST = 4
) (
  input  logic unsigned [DATA_WIDTH-1:0] A, // This is a test
  input  logic unsigned [DATA_WIDTH-1:0] B,
  output logic unsigned [DATA_WIDTH:0]   X
);

  assign X = A + B;

  // This instance was added to test a bug
  logic a_port;
  logic b_port;
  assign a_port = 'd0;

  test_module u_test_module(
      .test_input(a_port),
      .test_output(b_port)
      );

  // Dump waves
  initial begin
    $dumpfile("dump.vcd");
    $dumpvars(1, adder);
  end

endmodule
