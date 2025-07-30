module matrix (
  input  wire                main_clk_i,
  input  wire                main_rst_an_i, // Async Reset (Low-Active)
  output logic               intf_rx_o,
  input  wire                intf_tx_i,
  input  wire  [1:0]         bus_a_trans_i,
  input  wire  [31:0]        bus_a_addr_i,
  input  wire                bus_a_write_i,
  input  wire  [31:0]        bus_a_wdata_i,
  output logic               bus_a_ready_o,
  output logic               bus_a_resp_o,
  output logic [31:0]        bus_a_rdata_o,

  input  wire  [1:0]         bus_b_trans_i,
  input  wire  [31:0]        bus_b_addr_i,
  input  wire                bus_b_write_i,
  input  wire  [31:0]        bus_b_wdata_i,
  output logic               bus_b_ready_o,
  output logic               bus_b_resp_o,
  output logic [31:0]        bus_b_rdata_o,

  output wire  [1:0]         bus_c_trans_o,
  output wire  [31:0]        bus_c_addr_o,
  output wire                bus_c_write_o,
  output wire  [31:0]        bus_c_wdata_o,
  input  logic               bus_c_ready_i,
  input  logic               bus_c_resp_i,
  input  logic [31:0]        bus_c_rdata_i,

  input  wire  [1:0]         bus_m0_trans,
  input  wire  [31:0]        bus_m0_addr,
  input  wire                bus_m0_write,
  input  wire  [31:0]        bus_m0_wdata,
  output logic               bus_m0_ready,
  output logic               bus_m0_resp,
  output logic [31:0]        bus_m0_rdata,

  output wire  [1:0]         bus_s0_trans,
  output wire  [31:0]        bus_s0_addr,
  output wire                bus_s0_write,
  output wire  [31:0]        bus_s0_wdata,
  input  logic               bus_s0_ready,
  input  logic               bus_s0_resp,
  input  logic [31:0]        bus_s0_rdata
);


endmodule // matrix
