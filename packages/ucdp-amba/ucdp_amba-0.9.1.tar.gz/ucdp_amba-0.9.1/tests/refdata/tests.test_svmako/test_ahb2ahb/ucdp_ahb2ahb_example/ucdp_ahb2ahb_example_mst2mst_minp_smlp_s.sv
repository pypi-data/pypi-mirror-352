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
// Module:     ucdp_amba.ucdp_ahb2ahb_example_mst2mst_minp_smlp_s
// Data Model: ucdp_amba.ucdp_ahb2ahb.UcdpAhb2ahbMod
//
//
// Converting Master to Master
//
// Signal    Src Tgt Conv
// hwrite     x   x  forward
// htrans     x   x  forward
// hsize      x   x  forward
// hresp      x   x  forward
// hsel       -   -  n/a
// haddr      x   x  forward
// hwdata     x   x  forward
// hrdata     x   x  forward
// hwstrb     -   x  tie-off
// hburst     -   x  tie-off
// hnonsec    -   x  tie-off
// hmastlock  -   x  tie-off
// hauser     -   -  n/a
// hwuser     -   -  n/a
// hruser     -   -  n/a
// hbuser     -   -  n/a
// hmaster    -   x  tie-off
// hexcl      -   x  tie-off
// hexokay    -   x  ignore
// hready     x   x  forward
// hreadyout  -   -  n/a
// hprot      -   x  tie-off to constant
//
// =============================================================================

`begin_keywords "1800-2009"
`default_nettype none  // implicit wires are forbidden

module ucdp_ahb2ahb_example_mst2mst_minp_smlp_s ( // ucdp_amba.ucdp_ahb2ahb.UcdpAhb2ahbMod
  // ahb_src_i: AHB Source
  input  wire  [1:0]  ahb_src_htrans_i,    // AHB Transfer Type
  input  wire  [31:0] ahb_src_haddr_i,     // AHB Bus Address
  input  wire         ahb_src_hwrite_i,    // AHB Write Enable
  input  wire  [2:0]  ahb_src_hsize_i,     // AHB Size
  input  wire  [31:0] ahb_src_hwdata_i,    // AHB Data
  output logic        ahb_src_hready_o,    // AHB Transfer Done
  output logic        ahb_src_hresp_o,     // AHB Response Error
  output logic [31:0] ahb_src_hrdata_o,    // AHB Data
  // ahb_tgt_o: AHB Target
  output logic [1:0]  ahb_tgt_htrans_o,    // AHB Transfer Type
  output logic [31:0] ahb_tgt_haddr_o,     // AHB Bus Address
  output logic        ahb_tgt_hwrite_o,    // AHB Write Enable
  output logic [2:0]  ahb_tgt_hsize_o,     // AHB Size
  output logic [2:0]  ahb_tgt_hburst_o,    // AHB Burst Type
  output logic [3:0]  ahb_tgt_hprot_o,     // AHB Transfer Protection
  output logic        ahb_tgt_hnonsec_o,   // AHB Secure Transfer
  output logic        ahb_tgt_hmastlock_o, // AHB Locked Sequence Enable
  output logic [31:0] ahb_tgt_hwdata_o,    // AHB Data
  output logic [3:0]  ahb_tgt_hwstrb_o,    // AHB Write Strobe
  output logic        ahb_tgt_hexcl_o,     // AHB Exclusive Transfer
  output logic [3:0]  ahb_tgt_hmaster_o,   // AHB Master ID
  input  wire         ahb_tgt_hready_i,    // AHB Transfer Done
  input  wire         ahb_tgt_hresp_i,     // AHB Response Error
  input  wire         ahb_tgt_hexokay_i,   // AHB Exclusive Response
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

  // === hburst handling ================
  assign ahb_tgt_hburst_o = ahb_burst_incr_e;


  // === hxdata handling ================
  // just forward read/write data
  assign ahb_tgt_hwdata_o = ahb_src_hwdata_i;
  assign ahb_src_hrdata_o = ahb_tgt_hrdata_i;

  // === hwstrb handling =================
  assign ahb_tgt_hwstrb_o = 4'hF;

  // === hready handling ================
  assign ahb_src_hready_o = ahb_tgt_hready_i;

  // === hprot handling =================
  assign ahb_tgt_hprot_o = 4'h1;

  // === hnonsec handling ================
  assign ahb_tgt_hnonsec_o = 1'b0;

  // === hmastlock handling ================
  assign ahb_tgt_hmastlock_o = 1'b0;

  // === hexcl handling ================
  assign ahb_tgt_hexcl_o = 1'b1;


  // === hmaster handling: tie-off =================
  assign ahb_tgt_hmaster_o = 4'h1;






endmodule // ucdp_ahb2ahb_example_mst2mst_minp_smlp_s

`default_nettype wire
`end_keywords

// =============================================================================
//
//   @generated @fully-generated
//
//   THIS FILE IS GENERATED!!! DO NOT EDIT MANUALLY. CHANGES ARE LOST.
//
// =============================================================================
