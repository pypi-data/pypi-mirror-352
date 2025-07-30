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
// Module:     ucdp_amba.ucdp_ahb2ahb_example_slv2slv_minp_minp_p
// Data Model: ucdp_amba.ucdp_ahb2ahb.UcdpAhb2ahbMod
//
//
// No conversion, just feed-through.
//
// =============================================================================

`begin_keywords "1800-2009"
`default_nettype none  // implicit wires are forbidden

module ucdp_ahb2ahb_example_slv2slv_minp_minp_p ( // ucdp_amba.ucdp_ahb2ahb.UcdpAhb2ahbMod
  // ahb_src_i: AHB Source
  input  wire         ahb_src_hsel_i,      // AHB Slave Select
  input  wire  [31:0] ahb_src_haddr_i,     // AHB Bus Address
  input  wire         ahb_src_hwrite_i,    // AHB Write Enable
  input  wire  [1:0]  ahb_src_htrans_i,    // AHB Transfer Type
  input  wire  [2:0]  ahb_src_hsize_i,     // AHB Size
  input  wire  [31:0] ahb_src_hwdata_i,    // AHB Data
  input  wire         ahb_src_hready_i,    // AHB Transfer Done to Slave
  output logic        ahb_src_hreadyout_o, // AHB Transfer Done from Slave
  output logic        ahb_src_hresp_o,     // AHB Response Error
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





  // TODO: handle async


  // === standard forwarding ============
  assign ahb_tgt_htrans_o = ahb_src_htrans_i;
  assign ahb_tgt_hwrite_o = ahb_src_hwrite_i;
  assign ahb_tgt_hsize_o = ahb_src_hsize_i;
  assign ahb_src_hresp_o = ahb_tgt_hresp_i;

  // === haddr handling =================
  assign ahb_tgt_haddr_o = ahb_src_haddr_i;


  // === hsel handling ==================
  assign ahb_tgt_hsel_o = ahb_src_hsel_i;

  // === hxdata handling ================
  // just forward read/write data
  assign ahb_tgt_hwdata_o = ahb_src_hwdata_i;
  assign ahb_src_hrdata_o = ahb_tgt_hrdata_i;


  // === hready handling ================
  assign ahb_tgt_hready_o = ahb_src_hready_i;
  assign ahb_src_hreadyout_o = ahb_tgt_hreadyout_i;












endmodule // ucdp_ahb2ahb_example_slv2slv_minp_minp_p

`default_nettype wire
`end_keywords

// =============================================================================
//
//   @generated @fully-generated
//
//   THIS FILE IS GENERATED!!! DO NOT EDIT MANUALLY. CHANGES ARE LOST.
//
// =============================================================================
