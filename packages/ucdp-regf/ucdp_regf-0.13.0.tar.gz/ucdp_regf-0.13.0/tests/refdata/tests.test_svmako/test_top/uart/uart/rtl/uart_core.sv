// GENERATE INPLACE BEGIN fileheader() =========================================
//
// Module:     uart.uart_core
// Data Model: uart.uart.UartCoreMod
//
// GENERATE INPLACE END fileheader =============================================

// GENERATE INPLACE BEGIN beginmod() ===========================================
module uart_core ( // uart.uart.UartCoreMod
  // main_i: Clock and Reset
  input  wire  main_clk_i,    // Clock
  input  wire  main_rst_an_i, // Async Reset (Low-Active)
  // -
  output logic busy_o         // Busy
);
// GENERATE INPLACE END beginmod ===============================================

// GENERATE INPLACE BEGIN endmod() =============================================
endmodule // uart_core
// GENERATE INPLACE END endmod =================================================
