"""
Quick test script to verify emoji and Unicode display
"""

print("=" * 80)
print("EMOJI & UNICODE DISPLAY TEST")
print("=" * 80)

print("\n[BASIC EMOJIS]")
print("✅ Checkmark")
print("❌ Cross")
print("⚠️  Warning")
print("📊 Chart")
print("🔍 Search")
print("🎯 Target")
print("💡 Lightbulb")
print("🚀 Rocket")

print("\n[SPECIAL CHARACTERS]")
print("• Bullet point")
print("→ Arrow")
print("© Copyright")
print("™ Trademark")
print("€ Euro")
print("£ Pound")

print("\n[ACCENTED CHARACTERS]")
print("Nikola Jokić")
print("Luka Dončić")
print("Café")
print("naïve")
print("résumé")

print("\n[BOX DRAWING]")
print("┌─────────────────┐")
print("│  Test Box       │")
print("└─────────────────┘")

print("\n[PROGRESS BAR]")
print("█████████████████░░░ 85%")

print("\n" + "=" * 80)
if all(c in str(c.encode('utf-8')) or True for c in "✅🎯"):
    print("✅ If you can see emojis above, UTF-8 is working!")
else:
    print("[OK] If you can see emojis above, UTF-8 is working!")
print("=" * 80)
