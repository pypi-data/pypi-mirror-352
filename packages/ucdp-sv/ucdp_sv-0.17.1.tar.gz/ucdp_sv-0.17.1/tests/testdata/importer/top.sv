// =============================================================================
//
//   @generated
//
//   THIS FILE IS GENERATED!!! DO NOT EDIT MANUALLY. CHANGES ARE LOST.
//
// =============================================================================
//
//  MIT License
//
//  Copyright (c) 2024 nbiotcloud
//
//  Permission is hereby granted, free of charge, to any person obtaining a copy
//  of this software and associated documentation files (the "Software"), to deal
//  in the Software without restriction, including without limitation the rights
//  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
//  copies of the Software, and to permit persons to whom the Software is
//  furnished to do so, subject to the following conditions:
//
//  The above copyright notice and this permission notice shall be included in all
//  copies or substantial portions of the Software.
//
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
//  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
//  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
//  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
//  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
//  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
//  SOFTWARE.
//
// =============================================================================

`begin_keywords "1800-2009"
`default_nettype none  // implicit wires are forbidden

module top #(
  parameter integer               param_p   = 10,
  parameter integer               width_p   = $clog2(param_p + 1),
  parameter logic   [param_p-1:0] default_p = {param_p {1'b0}}
) (
  // main_i
  input  wire                main_clk_i,
  input  wire                main_rst_an_i, // Async Reset (Low-Active)
  // intf_i: RX/TX
  output logic               intf_rx_o,
  input  wire                intf_tx_i,
  // bus_i
  input  wire  [1:0]         bus_trans_i,
  input  wire  [31:0]        bus_addr_i,
  input  wire                bus_write_i,
  input  wire  [31:0]        bus_wdata_i,
  output logic               bus_ready_o,
  output logic               bus_resp_o,
  output logic [31:0]        bus_rdata_o,
  input  wire  [param_p-1:0] data_i,
  output logic [width_p-1:0] cnt_o,
  `ifdef ASIC
  output logic [8:0]         brick_o,
  `endif // ASIC
  // key_i
  input                      key_valid_i,
  output logic               key_accept,
  input  wire  [8:0]         key_data,
  inout  wire  [3:0]         bidir
  `ifdef ASIC
  ,
  output logic [8:0]         value_o
  `endif // ASIC
);


endmodule // top

`default_nettype wire
`end_keywords

// =============================================================================
//
//   @generated
//
//   THIS FILE IS GENERATED!!! DO NOT EDIT MANUALLY. CHANGES ARE LOST.
//
// =============================================================================
