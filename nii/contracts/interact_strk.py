#!/usr/bin/env python3
"""
STRK Token Interaction Script

This script demonstrates native Python interaction with the STRK token contract:
- Deploy contract
- Mint tokens
- Transfer tokens
- Burn tokens
- Check balances and events
"""

from strk import STRKToken


def main():
    """Main interaction demonstration."""
    print("🚀 STRK Token Native Python Interaction Demo")
    print("=" * 50)
    
    # Contract deployment
    print("\n📋 1. DEPLOYING STRK TOKEN CONTRACT")
    owner = "0x742d35Cc6634C0532925a3b8D4C9db96c4b4c1e3"
    alice = "0x8ba1f109551bD432803012645Hac136c9.eff"
    bob = "0x1234567890123456789012345678901234567890"
    
    # Deploy with 1M initial supply
    strk = STRKToken(owner, initial_supply=1000000)
    
    print(f"✅ Contract deployed!")
    print(f"   Owner: {owner}")
    print(f"   Token Name: {strk.name}")
    print(f"   Token Symbol: {strk.symbol}")
    print(f"   Decimals: {strk.decimals}")
    print(f"   Total Supply: {strk.to_tokens(strk.total_supply):,.0f} STRK")
    print(f"   Owner Balance: {strk.to_tokens(strk.balance_of(owner)):,.0f} STRK")
    
    # Minting tokens
    print("\n🪙 2. MINTING TOKENS")
    mint_amount = strk.to_wei(50000)  # 50,000 STRK
    
    print(f"Minting {strk.to_tokens(mint_amount):,.0f} STRK to Alice...")
    success = strk.mint(owner, alice, mint_amount)
    
    if success:
        print(f"✅ Mint successful!")
        print(f"   Alice Balance: {strk.to_tokens(strk.balance_of(alice)):,.0f} STRK")
        print(f"   New Total Supply: {strk.to_tokens(strk.total_supply):,.0f} STRK")
    else:
        print("❌ Mint failed!")
    
    # Transfer tokens
    print("\n💸 3. TRANSFERRING TOKENS")
    transfer_amount = strk.to_wei(25000)  # 25,000 STRK
    
    print(f"Alice transferring {strk.to_tokens(transfer_amount):,.0f} STRK to Bob...")
    success = strk.transfer(alice, bob, transfer_amount)
    
    if success:
        print(f"✅ Transfer successful!")
        print(f"   Alice Balance: {strk.to_tokens(strk.balance_of(alice)):,.0f} STRK")
        print(f"   Bob Balance: {strk.to_tokens(strk.balance_of(bob)):,.0f} STRK")
    else:
        print("❌ Transfer failed!")
    
    # Approve and transfer from
    print("\n🔐 4. APPROVAL & TRANSFER FROM")
    approve_amount = strk.to_wei(10000)  # 10,000 STRK
    
    print(f"Bob approving Owner to spend {strk.to_tokens(approve_amount):,.0f} STRK...")
    success = strk.approve(bob, owner, approve_amount)
    
    if success:
        print(f"✅ Approval successful!")
        print(f"   Allowance: {strk.to_tokens(strk.allowance(bob, owner)):,.0f} STRK")
        
        # Owner transfers from Bob to Alice
        transfer_from_amount = strk.to_wei(5000)  # 5,000 STRK
        print(f"Owner transferring {strk.to_tokens(transfer_from_amount):,.0f} STRK from Bob to Alice...")
        
        success = strk.transfer_from(owner, bob, alice, transfer_from_amount)
        if success:
            print(f"✅ Transfer from successful!")
            print(f"   Alice Balance: {strk.to_tokens(strk.balance_of(alice)):,.0f} STRK")
            print(f"   Bob Balance: {strk.to_tokens(strk.balance_of(bob)):,.0f} STRK")
            print(f"   Remaining Allowance: {strk.to_tokens(strk.allowance(bob, owner)):,.0f} STRK")
        else:
            print("❌ Transfer from failed!")
    else:
        print("❌ Approval failed!")
    
    # Burning tokens
    print("\n🔥 5. BURNING TOKENS")
    burn_amount = strk.to_wei(10000)  # 10,000 STRK
    
    print(f"Alice burning {strk.to_tokens(burn_amount):,.0f} STRK...")
    alice_balance_before = strk.balance_of(alice)
    success = strk.burn(alice, burn_amount)
    
    if success:
        print(f"✅ Burn successful!")
        print(f"   Alice Balance Before: {strk.to_tokens(alice_balance_before):,.0f} STRK")
        print(f"   Alice Balance After: {strk.to_tokens(strk.balance_of(alice)):,.0f} STRK")
        print(f"   New Total Supply: {strk.to_tokens(strk.total_supply):,.0f} STRK")
    else:
        print("❌ Burn failed!")
    
    # Add new minter
    print("\n👑 6. MINTER MANAGEMENT")
    print(f"Adding Alice as a minter...")
    success = strk.add_minter(owner, alice)
    
    if success:
        print(f"✅ Alice added as minter!")
        print(f"   Alice is minter: {strk.is_minter(alice)}")
        
        # Alice mints tokens for herself
        alice_mint_amount = strk.to_wei(15000)  # 15,000 STRK
        print(f"Alice minting {strk.to_tokens(alice_mint_amount):,.0f} STRK for herself...")
        
        success = strk.mint(alice, alice, alice_mint_amount)
        if success:
            print(f"✅ Alice's mint successful!")
            print(f"   Alice Balance: {strk.to_tokens(strk.balance_of(alice)):,.0f} STRK")
        else:
            print("❌ Alice's mint failed!")
    else:
        print("❌ Failed to add Alice as minter!")
    
    # Final balances
    print("\n📊 7. FINAL BALANCES")
    print(f"Owner Balance: {strk.to_tokens(strk.balance_of(owner)):,.0f} STRK")
    print(f"Alice Balance: {strk.to_tokens(strk.balance_of(alice)):,.0f} STRK")
    print(f"Bob Balance: {strk.to_tokens(strk.balance_of(bob)):,.0f} STRK")
    print(f"Total Supply: {strk.to_tokens(strk.total_supply):,.0f} STRK")
    
    # Event logs
    print("\n📜 8. EVENT LOGS")
    events = strk.get_events()
    print(f"Total Events: {len(events)}")
    
    for i, event in enumerate(events[-5:], 1):  # Show last 5 events
        if event["type"] == "Transfer":
            from_addr = event["from"][:10] + "..." if len(event["from"]) > 10 else event["from"]
            to_addr = event["to"][:10] + "..." if len(event["to"]) > 10 else event["to"]
            amount = strk.to_tokens(event["value"])
            print(f"   {len(events)-5+i}. Transfer: {from_addr} → {to_addr} ({amount:,.0f} STRK)")
        elif event["type"] == "Approval":
            owner_addr = event["owner"][:10] + "..." if len(event["owner"]) > 10 else event["owner"]
            spender_addr = event["spender"][:10] + "..." if len(event["spender"]) > 10 else event["spender"]
            amount = strk.to_tokens(event["value"])
            print(f"   {len(events)-5+i}. Approval: {owner_addr} → {spender_addr} ({amount:,.0f} STRK)")
    
    print("\n🎉 STRK Token interaction demo completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
