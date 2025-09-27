#!/usr/bin/env python3
"""
STRK Token Core Operations: Mint, Burn, Send

Focused demonstration of the three core token operations.
"""

from strk import STRKToken


def print_balances(strk, accounts):
    """Print current balances for all accounts."""
    print("\n💰 Current Balances:")
    for name, address in accounts.items():
        balance = strk.to_tokens(strk.balance_of(address))
        print(f"   {name}: {balance:,.2f} STRK")
    print(f"   Total Supply: {strk.to_tokens(strk.total_supply):,.2f} STRK")


def main():
    """Demonstrate mint, burn, and send operations."""
    print("🚀 STRK Token Operations: MINT → SEND → BURN")
    print("=" * 50)
    
    # Setup accounts
    accounts = {
        "Owner": "0x742d35Cc6634C0532925a3b8D4C9db96c4b4c1e3",
        "Alice": "0x8ba1f109551bD432803012645Hac136c9.eff",
        "Bob": "0x1234567890123456789012345678901234567890",
        "Charlie": "0x9876543210987654321098765432109876543210"
    }
    
    # Deploy contract with zero initial supply for clean demo
    print("\n📋 Deploying STRK Token (0 initial supply)...")
    strk = STRKToken(accounts["Owner"], initial_supply=0)
    print(f"✅ Contract deployed! Owner: {accounts['Owner'][:10]}...")
    
    print_balances(strk, accounts)
    
    # === MINT OPERATIONS ===
    print("\n" + "="*20 + " MINTING " + "="*20)
    
    # Mint to Alice
    mint_amount_alice = strk.to_wei(100000)  # 100,000 STRK
    print(f"\n🪙 Minting {strk.to_tokens(mint_amount_alice):,.0f} STRK to Alice...")
    success = strk.mint(accounts["Owner"], accounts["Alice"], mint_amount_alice)
    
    if success:
        print("✅ Mint to Alice successful!")
    else:
        print("❌ Mint to Alice failed!")
    
    print_balances(strk, accounts)
    
    # Mint to Bob
    mint_amount_bob = strk.to_wei(75000)  # 75,000 STRK
    print(f"\n🪙 Minting {strk.to_tokens(mint_amount_bob):,.0f} STRK to Bob...")
    success = strk.mint(accounts["Owner"], accounts["Bob"], mint_amount_bob)
    
    if success:
        print("✅ Mint to Bob successful!")
    else:
        print("❌ Mint to Bob failed!")
    
    print_balances(strk, accounts)
    
    # === SEND OPERATIONS ===
    print("\n" + "="*20 + " SENDING " + "="*20)
    
    # Alice sends to Charlie
    send_amount_1 = strk.to_wei(25000)  # 25,000 STRK
    print(f"\n💸 Alice sending {strk.to_tokens(send_amount_1):,.0f} STRK to Charlie...")
    success = strk.transfer(accounts["Alice"], accounts["Charlie"], send_amount_1)
    
    if success:
        print("✅ Alice → Charlie transfer successful!")
    else:
        print("❌ Alice → Charlie transfer failed!")
    
    print_balances(strk, accounts)
    
    # Bob sends to Alice
    send_amount_2 = strk.to_wei(30000)  # 30,000 STRK
    print(f"\n💸 Bob sending {strk.to_tokens(send_amount_2):,.0f} STRK to Alice...")
    success = strk.transfer(accounts["Bob"], accounts["Alice"], send_amount_2)
    
    if success:
        print("✅ Bob → Alice transfer successful!")
    else:
        print("❌ Bob → Alice transfer failed!")
    
    print_balances(strk, accounts)
    
    # Charlie sends to Bob
    send_amount_3 = strk.to_wei(10000)  # 10,000 STRK
    print(f"\n💸 Charlie sending {strk.to_tokens(send_amount_3):,.0f} STRK to Bob...")
    success = strk.transfer(accounts["Charlie"], accounts["Bob"], send_amount_3)
    
    if success:
        print("✅ Charlie → Bob transfer successful!")
    else:
        print("❌ Charlie → Bob transfer failed!")
    
    print_balances(strk, accounts)
    
    # === BURN OPERATIONS ===
    print("\n" + "="*20 + " BURNING " + "="*20)
    
    # Alice burns some tokens
    burn_amount_1 = strk.to_wei(20000)  # 20,000 STRK
    alice_balance_before = strk.balance_of(accounts["Alice"])
    print(f"\n🔥 Alice burning {strk.to_tokens(burn_amount_1):,.0f} STRK...")
    success = strk.burn(accounts["Alice"], burn_amount_1)
    
    if success:
        print("✅ Alice burn successful!")
        print(f"   Burned: {strk.to_tokens(burn_amount_1):,.0f} STRK")
    else:
        print("❌ Alice burn failed!")
    
    print_balances(strk, accounts)
    
    # Bob burns some tokens
    burn_amount_2 = strk.to_wei(15000)  # 15,000 STRK
    print(f"\n🔥 Bob burning {strk.to_tokens(burn_amount_2):,.0f} STRK...")
    success = strk.burn(accounts["Bob"], burn_amount_2)
    
    if success:
        print("✅ Bob burn successful!")
        print(f"   Burned: {strk.to_tokens(burn_amount_2):,.0f} STRK")
    else:
        print("❌ Bob burn failed!")
    
    print_balances(strk, accounts)
    
    # Charlie burns remaining tokens
    charlie_balance = strk.balance_of(accounts["Charlie"])
    if charlie_balance > 0:
        print(f"\n🔥 Charlie burning all remaining tokens ({strk.to_tokens(charlie_balance):,.0f} STRK)...")
        success = strk.burn(accounts["Charlie"], charlie_balance)
        
        if success:
            print("✅ Charlie burn successful!")
            print(f"   Burned: {strk.to_tokens(charlie_balance):,.0f} STRK")
        else:
            print("❌ Charlie burn failed!")
    
    print_balances(strk, accounts)
    
    # === SUMMARY ===
    print("\n" + "="*20 + " SUMMARY " + "="*20)
    total_minted = mint_amount_alice + mint_amount_bob
    total_burned = burn_amount_1 + burn_amount_2 + charlie_balance
    
    print(f"📊 Operation Summary:")
    print(f"   Total Minted: {strk.to_tokens(total_minted):,.0f} STRK")
    print(f"   Total Burned: {strk.to_tokens(total_burned):,.0f} STRK")
    print(f"   Net Supply: {strk.to_tokens(strk.total_supply):,.0f} STRK")
    print(f"   Transfers: 3 successful transfers")
    
    # Show recent events
    print(f"\n📜 Recent Events:")
    events = strk.get_events()
    for event in events[-3:]:  # Last 3 events
        if event["type"] == "Transfer":
            from_short = "0x000..." if event["from"] == "0x0000000000000000000000000000000000000000" else event["from"][:8] + "..."
            to_short = "0x000..." if event["to"] == "0x0000000000000000000000000000000000000000" else event["to"][:8] + "..."
            amount = strk.to_tokens(event["value"])
            
            if event["from"] == "0x0000000000000000000000000000000000000000":
                print(f"   🪙 MINT: {amount:,.0f} STRK → {to_short}")
            elif event["to"] == "0x0000000000000000000000000000000000000000":
                print(f"   🔥 BURN: {amount:,.0f} STRK from {from_short}")
            else:
                print(f"   💸 SEND: {amount:,.0f} STRK from {from_short} → {to_short}")
    
    print(f"\n🎉 All operations completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()
