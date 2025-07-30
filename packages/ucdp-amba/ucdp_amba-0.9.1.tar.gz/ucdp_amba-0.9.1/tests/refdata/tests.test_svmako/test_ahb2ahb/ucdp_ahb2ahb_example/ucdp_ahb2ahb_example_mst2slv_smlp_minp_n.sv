// =============================================================================
//
//   @generated @fully-generated
//
//   THIS FILE IS GENERATED!!! DO NOT EDIT MANUALLY. CHANGES ARE LOST.
//
// =============================================================================
//
//  MIT License
//
//  Copyright (c) 2024-2025 nbiotcloud
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
//
// Module:     ucdp_amba.ucdp_ahb2ahb_example_mst2slv_smlp_minp_n
// Data Model: ucdp_amba.ucdp_ahb2ahb.UcdpAhb2ahbMod
//
//
// Converting Master to Slave
//
// Signal    Src Tgt Conv
// hwrite     x   x  forward
// htrans     x   x  forward
// hsize      x   x  forward
// hresp      x   x  forward
// hsel       -   x  tie-off
// haddr      x   x  forward
// hwdata     x   x  forward
// hrdata     x   x  forward
// hwstrb     x   -  ignore
// hburst     x   -  ignore
// hnonsec    x   -  ignore
// hmastlock  x   -  ignore
// hauser     -   -  n/a
// hwuser     -   -  n/a
// hruser     -   -  n/a
// hbuser     -   -  n/a
// hmaster    x   -  ignore
// hexcl      x   -  ignore
// hexokay    x   -  tie-off
// hready     x   x  convert
// hreadyout  -   x  convert
// hprot      x   -  ignore
//
// =============================================================================

`begin_keywords "1800-2009"
`default_nettype none  // implicit wires are forbidden

module ucdp_ahb2ahb_example_mst2slv_smlp_minp_n ( // ucdp_amba.ucdp_ahb2ahb.UcdpAhb2ahbMod
  // ahb_src_i: AHB Source
  input  wire  [1:0]  ahb_src_htrans_i,    // AHB Transfer Type
  input  wire  [31:0] ahb_src_haddr_i,     // AHB Bus Address
  input  wire         ahb_src_hwrite_i,    // AHB Write Enable
  input  wire  [2:0]  ahb_src_hsize_i,     // AHB Size
  input  wire  [2:0]  ahb_src_hburst_i,    // AHB Burst Type
  input  wire  [3:0]  ahb_src_hprot_i,     // AHB Transfer Protection
  input  wire         ahb_src_hnonsec_i,   // AHB Secure Transfer
  input  wire         ahb_src_hmastlock_i, // AHB Locked Sequence Enable
  input  wire  [31:0] ahb_src_hwdata_i,    // AHB Data
  input  wire  [3:0]  ahb_src_hwstrb_i,    // AHB Write Strobe
  input  wire         ahb_src_hexcl_i,     // AHB Exclusive Transfer
  input  wire  [3:0]  ahb_src_hmaster_i,   // AHB Master ID
  output logic        ahb_src_hready_o,    // AHB Transfer Done
  output logic        ahb_src_hresp_o,     // AHB Response Error
  output logic        ahb_src_hexokay_o,   // AHB Exclusive Response
  output logic [31:0] ahb_src_hrdata_o,    // AHB Data
  // ahb_tgt_o: AHB Target
  output logic        ahb_tgt_hsel_o,      // AHB Slave Select
  output logic [31:0] ahb_tgt_haddr_o,     // AHB Bus Address
  output logic        ahb_tgt_hwrite_o,    // AHB Write Enable
  output logic [1:0]  ahb_tgt_htrans_o,    // AHB Transfer Type
  output logic [2:0]  ahb_tgt_hsize_o,     // AHB Size
  output logic [31:0] ahb_tgt_hwdata_o,    // AHB Data
  output logic        ahb_tgt_hready_o,    // AHB Transfer Done to Slave
  input  wire         ahb_tgt_hreadyout_i, // AHB Transfer Done from Slave
  input  wire         ahb_tgt_hresp_i,     // AHB Response Error
  input  wire  [31:0] ahb_tgt_hrdata_i     // AHB Data
);




  // ------------------------------------------------------
  //  Local Parameter
  // ------------------------------------------------------
  // ahb_trans
  localparam integer       ahb_trans_width_p   = 2;    // Width in Bits
  localparam logic   [1:0] ahb_trans_min_p     = 2'h0; // AHB Transfer Type
  localparam logic   [1:0] ahb_trans_max_p     = 2'h3; // AHB Transfer Type
  localparam logic   [1:0] ahb_trans_idle_e    = 2'h0; // No transfer
  localparam logic   [1:0] ahb_trans_busy_e    = 2'h1; // Idle cycle within transfer
  localparam logic   [1:0] ahb_trans_nonseq_e  = 2'h2; // Single transfer or first transfer of a burst
  localparam logic   [1:0] ahb_trans_seq_e     = 2'h3; // Consecutive transfers of a burst
  localparam logic   [1:0] ahb_trans_default_p = 2'h0; // AHB Transfer Type
  // ahb_burst
  localparam integer       ahb_burst_width_p   = 3;    // Width in Bits
  localparam logic   [2:0] ahb_burst_min_p     = 3'h0; // AHB Burst Type
  localparam logic   [2:0] ahb_burst_max_p     = 3'h7; // AHB Burst Type
  localparam logic   [2:0] ahb_burst_single_e  = 3'h0; // Single transfer
  localparam logic   [2:0] ahb_burst_incr_e    = 3'h1; // Incrementing burst of unspecified length
  localparam logic   [2:0] ahb_burst_wrap4_e   = 3'h2; // 4-beat wrapping burst
  localparam logic   [2:0] ahb_burst_incr4_e   = 3'h3; // 4-beat incrementing burst
  localparam logic   [2:0] ahb_burst_wrap8_e   = 3'h4; // 8-beat wrapping burst
  localparam logic   [2:0] ahb_burst_incr8_e   = 3'h5; // 8-beat incrementing burst
  localparam logic   [2:0] ahb_burst_wrap16_e  = 3'h6; // 16-beat wrapping burst
  localparam logic   [2:0] ahb_burst_incr16_e  = 3'h7; // 16-beat incrementing burst
  localparam logic   [2:0] ahb_burst_default_p = 3'h0; // AHB Burst Type



  // TODO: handle async


  // === standard forwarding ============
  assign ahb_tgt_htrans_o = ahb_src_htrans_i;
  assign ahb_tgt_hwrite_o = ahb_src_hwrite_i;
  assign ahb_tgt_hsize_o = ahb_src_hsize_i;
  assign ahb_src_hresp_o = ahb_tgt_hresp_i;

  // === haddr handling =================
  assign ahb_tgt_haddr_o = ahb_src_haddr_i;


  // === hsel handling ==================
  assign ahb_tgt_hsel_o = 1'b1;

  // === hxdata handling ================
  // just forward read/write data
  assign ahb_tgt_hwdata_o = ahb_src_hwdata_i;
  assign ahb_src_hrdata_o = ahb_tgt_hrdata_i;


  // === hready handling ================
  assign ahb_src_hready_o = ahb_tgt_hreadyout_i;
  assign ahb_tgt_hready_o = ahb_tgt_hreadyout_i;





  // === hexokay handling ================
  assign ahb_src_hexokay_o = 1'b0;







endmodule // ucdp_ahb2ahb_example_mst2slv_smlp_minp_n

`default_nettype wire
`end_keywords

// =============================================================================
//
//   @generated @fully-generated
//
//   THIS FILE IS GENERATED!!! DO NOT EDIT MANUALLY. CHANGES ARE LOST.
//
// =============================================================================
