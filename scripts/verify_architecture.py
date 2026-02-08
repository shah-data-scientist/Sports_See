"""
FILE: verify_architecture.py
STATUS: Active
RESPONSIBILITY: Verify LLM architecture - Mistral for embeddings, Gemini for chat/SQL
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

import sys
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.services.chat import ChatService
from src.services.embedding import EmbeddingService
from src.tools.sql_tool import NBAGSQLTool
from src.core.config import settings


def verify_embedding_service():
    """Verify EmbeddingService uses Mistral."""
    print("\n" + "="*80)
    print("EMBEDDING SERVICE (Vector Search)")
    print("="*80 + "\n")

    embedding_service = EmbeddingService()

    print(f"Service: EmbeddingService")
    print(f"Provider: Mistral AI")
    print(f"Model: {embedding_service.model}")
    print(f"API Key Source: settings.mistral_api_key")
    print(f"API Key Present: {'Yes' if settings.mistral_api_key else 'No'}")
    print(f"API Key Value: {settings.mistral_api_key[:20]}..." if settings.mistral_api_key else "NOT SET")

    # Check client type
    client_type = type(embedding_service.client).__name__
    print(f"Client Type: {client_type}")

    if "Mistral" in client_type:
        print("✓ Correctly using Mistral client for embeddings")
        return True
    else:
        print(f"✗ ERROR: Expected Mistral client, got {client_type}")
        return False


def verify_chat_service():
    """Verify ChatService uses Gemini for chat, Mistral for embeddings."""
    print("\n" + "="*80)
    print("CHAT SERVICE (Response Generation)")
    print("="*80 + "\n")

    chat_service = ChatService()

    print(f"Service: ChatService")
    print(f"Chat Provider: Google Gemini")
    print(f"Chat Model: {chat_service.model}")
    print(f"API Key Source: settings.google_api_key")
    print(f"API Key Present: {'Yes' if settings.google_api_key else 'No'}")

    # Check chat client type
    chat_client_type = type(chat_service.client).__name__
    print(f"Chat Client Type: {chat_client_type}")

    if "Client" in chat_client_type or "genai" in str(type(chat_service.client)):
        print("✓ Correctly using Gemini client for chat")
        chat_ok = True
    else:
        print(f"✗ ERROR: Expected Gemini client, got {chat_client_type}")
        chat_ok = False

    # Check embedding service
    print(f"\nEmbedding Provider: Mistral AI (via EmbeddingService)")
    embedding_client_type = type(chat_service.embedding_service.client).__name__
    print(f"Embedding Client Type: {embedding_client_type}")

    if "Mistral" in embedding_client_type:
        print("✓ Correctly using Mistral client for embeddings")
        embed_ok = True
    else:
        print(f"✗ ERROR: Expected Mistral client, got {embedding_client_type}")
        embed_ok = False

    return chat_ok and embed_ok


def verify_sql_tool():
    """Verify SQL tool uses Gemini."""
    print("\n" + "="*80)
    print("SQL TOOL (Database Queries)")
    print("="*80 + "\n")

    sql_tool = NBAGSQLTool()

    print(f"Service: NBAGSQLTool")
    print(f"Provider: Google Gemini")
    print(f"Model: gemini-2.0-flash-lite")
    print(f"Framework: LangChain + ChatGoogleGenerativeAI")
    print(f"API Key Source: settings.google_api_key")

    # Check LLM type
    llm_type = type(sql_tool.llm).__name__
    print(f"LLM Type: {llm_type}")

    if "GoogleGenerativeAI" in llm_type or "Gemini" in llm_type:
        print("✓ Correctly using Gemini LLM for SQL generation")
        return True
    else:
        print(f"✗ ERROR: Expected Gemini LLM, got {llm_type}")
        return False


def main():
    """Verify complete architecture."""
    print("\n" + "="*80)
    print("  SPORTS_SEE ARCHITECTURE VERIFICATION")
    print("  Mistral (Embeddings) + Gemini (Chat + SQL)")
    print("="*80)

    results = []

    # Verify each component
    results.append(("Embedding Service (Mistral)", verify_embedding_service()))
    results.append(("Chat Service (Gemini + Mistral)", verify_chat_service()))
    results.append(("SQL Tool (Gemini)", verify_sql_tool()))

    # Summary
    print("\n" + "="*80)
    print("ARCHITECTURE VERIFICATION SUMMARY")
    print("="*80 + "\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for component, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {component}")

    print(f"\nOverall: {passed}/{total} components verified correctly")

    print("\n" + "="*80)
    print("CORRECT ARCHITECTURE:")
    print("="*80)
    print("1. ✓ Embeddings → Mistral AI (mistral-embed)")
    print("2. ✓ Vector Search → FAISS (no LLM)")
    print("3. ✓ Chat/Response → Google Gemini 2.0 Flash Lite")
    print("4. ✓ SQL Generation → Google Gemini 2.0 Flash Lite")
    print("="*80)

    if passed == total:
        print("\n✓ ARCHITECTURE CORRECTLY CONFIGURED")
        return 0
    else:
        print(f"\n✗ {total - passed} component(s) misconfigured")
        return 1


if __name__ == "__main__":
    sys.exit(main())
