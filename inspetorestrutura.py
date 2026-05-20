#!/usr/bin/env python3
"""
INSPETOR DE DATASETS
Descobre a estrutura dos arquivos CSV/JSON baixados
"""

import pandas as pd
from pathlib import Path
import json

CORPUS_DIR = Path("lexicons_corpus_misoginia")

def inspect_csv(file_path):
    """Inspeciona arquivo CSV"""
    print(f"\n📄 Arquivo: {file_path.name}")
    print("=" * 70)
    
    try:
        # Tentar ler com diferentes separadores
        for sep in [',', '\t', ';']:
            try:
                df = pd.read_csv(file_path, sep=sep, nrows=5)
                if len(df.columns) > 1:  # Se tiver mais de 1 coluna, achou o separador certo
                    print(f"✅ Separador detectado: '{sep}'")
                    break
            except:
                continue
        
        print(f"📊 Total de linhas: {len(pd.read_csv(file_path, sep=sep))}")
        print(f"📊 Total de colunas: {len(df.columns)}")
        print(f"\n🏷️  COLUNAS:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i}. {col}")
        
        print(f"\n📝 PREVIEW (primeiras 3 linhas):")
        print("-" * 70)
        print(df.head(3).to_string())
        
        print(f"\n📈 TIPOS DE DADOS:")
        print(df.dtypes.to_string())
        
        # Procurar colunas de rótulo
        label_cols = [col for col in df.columns if any(word in col.lower() for word in 
                      ['label', 'class', 'category', 'hate', 'toxic', 'offensive', 
                       'misogyny', 'sexism', 'sentiment'])]
        
        if label_cols:
            print(f"\n🎯 POSSÍVEIS COLUNAS DE RÓTULO:")
            for col in label_cols:
                print(f"   - {col}")
                print(f"     Valores únicos: {df[col].unique()}")
        
        # Procurar colunas de texto
        text_cols = [col for col in df.columns if any(word in col.lower() for word in 
                     ['text', 'comment', 'tweet', 'message', 'content', 'post'])]
        
        if text_cols:
            print(f"\n📝 POSSÍVEIS COLUNAS DE TEXTO:")
            for col in text_cols:
                print(f"   - {col}")
                print(f"     Exemplo: {df[col].iloc[0][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao ler: {e}")
        return False

def inspect_json(file_path):
    """Inspeciona arquivo JSON"""
    print(f"\n📄 Arquivo: {file_path.name}")
    print("=" * 70)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            print(f"✅ Tipo: Lista com {len(data)} itens")
            if data:
                print(f"\n🏷️  CHAVES DO PRIMEIRO ITEM:")
                for key in data[0].keys():
                    print(f"   - {key}")
                
                print(f"\n📝 PREVIEW (primeiro item):")
                print(json.dumps(data[0], indent=2, ensure_ascii=False)[:500])
        
        elif isinstance(data, dict):
            print(f"✅ Tipo: Dicionário")
            print(f"\n🏷️  CHAVES PRINCIPAIS:")
            for key in data.keys():
                print(f"   - {key}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao ler: {e}")
        return False

def scan_directory(directory):
    """Escaneia diretório recursivamente"""
    print("\n" + "=" * 70)
    print("🔍 ESCANEANDO DATASETS")
    print("=" * 70)
    
    found_files = []
    
    # Procurar arquivos CSV e JSON
    for ext in ['*.csv', '*.tsv', '*.json', '*.jsonl']:
        files = list(directory.rglob(ext))
        found_files.extend(files)
    
    if not found_files:
        print(f"\n❌ Nenhum arquivo encontrado em: {directory.absolute()}")
        print("\n💡 Verifique se os datasets foram baixados corretamente")
        return
    
    print(f"\n✅ Encontrados {len(found_files)} arquivos\n")
    
    # Inspecionar cada arquivo
    for file_path in found_files:
        if file_path.suffix in ['.csv', '.tsv']:
            inspect_csv(file_path)
        elif file_path.suffix in ['.json', '.jsonl']:
            inspect_json(file_path)
        
        print("\n" + "=" * 70)
    
    # Resumo final
    print("\n📋 RESUMO:")
    print("-" * 70)
    for file_path in found_files:
        relative_path = file_path.relative_to(directory)
        print(f"   {relative_path}")

def main():
    if not CORPUS_DIR.exists():
        print(f"❌ Diretório não encontrado: {CORPUS_DIR.absolute()}")
        print("\n💡 Certifique-se de que os datasets foram baixados")
        print(f"   Esperado em: {CORPUS_DIR.absolute()}")
        return
    
    scan_directory(CORPUS_DIR)
    
    print("\n" + "=" * 70)
    print("✅ INSPEÇÃO CONCLUÍDA!")
    print("=" * 70)
    print("\n🔜 PRÓXIMO PASSO:")
    print("   Use as informações acima para configurar o script de construção do léxico")

if __name__ == "__main__":
    main()

