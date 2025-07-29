#!/usr/bin/env python3
"""
Unified Models Manager
Łączy dane z Ollama i HuggingFace, zarządza modelami, wyszukuje i filtruje
"""

import json
import argparse
import sys
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import subprocess
import tempfile
import requests


class UnifiedModelsManager:
    def __init__(self):
        self.ollama_data = {}
        self.huggingface_data = {}
        self.combined_models = []

    def load_data(self, ollama_file: str = "ollama_models.json",
                  huggingface_file: str = "huggingface_models.json"):
        """Ładuje dane z plików JSON"""

        # Load Ollama data
        if os.path.exists(ollama_file):
            try:
                with open(ollama_file, 'r', encoding='utf-8') as f:
                    self.ollama_data = json.load(f)
                print(f"✅ Loaded {len(self.ollama_data.get('models', []))} Ollama models")
            except Exception as e:
                print(f"❌ Error loading Ollama data: {e}")
        else:
            print(f"⚠️ Ollama file {ollama_file} not found")

        # Load HuggingFace data
        if os.path.exists(huggingface_file):
            try:
                with open(huggingface_file, 'r', encoding='utf-8') as f:
                    self.huggingface_data = json.load(f)
                print(f"✅ Loaded {len(self.huggingface_data.get('models', []))} HuggingFace models")
            except Exception as e:
                print(f"❌ Error loading HuggingFace data: {e}")
        else:
            print(f"⚠️ HuggingFace file {huggingface_file} not found")

    def combine_models(self) -> List[Dict[str, Any]]:
        """Łączy modele z obu źródeł"""
        combined = []

        # Add Ollama models
        for model in self.ollama_data.get('models', []):
            model['availability'] = ['ollama']
            model['local_ready'] = True
            combined.append(model)

        # Add HuggingFace models
        for model in self.huggingface_data.get('models', []):
            model['availability'] = ['huggingface']
            if model.get('ollama_compatible', False):
                model['availability'].append('convertible_to_ollama')
            model['local_ready'] = model.get('gguf_available', False)
            combined.append(model)

        self.combined_models = combined
        return combined

    def search_models(self,
                      query: str = "",
                      source: str = "all",  # all, ollama, huggingface
                      task: str = "",
                      local_ready_only: bool = False,
                      min_downloads: int = 0,
                      size_limit_gb: Optional[float] = None) -> List[Dict[str, Any]]:
        """Zaawansowane wyszukiwanie modeli"""

        if not self.combined_models:
            self.combine_models()

        results = []
        query_lower = query.lower() if query else ""

        for model in self.combined_models:
            # Filter by source
            if source != "all":
                if source == "ollama" and model['source'] != 'ollama':
                    continue
                if source == "huggingface" and model['source'] != 'huggingface':
                    continue

            # Filter by local readiness
            if local_ready_only and not model.get('local_ready', False):
                continue

            # Filter by downloads
            downloads = model.get('downloads', 0) or model.get('pulls', 0)
            if isinstance(downloads, str):
                # Parse "1.2M" etc.
                try:
                    if 'M' in downloads:
                        downloads = float(downloads.replace('M', '')) * 1000000
                    elif 'k' in downloads or 'K' in downloads:
                        downloads = float(downloads.replace('k', '').replace('K', '')) * 1000
                    else:
                        downloads = float(downloads.split()[0])
                except:
                    downloads = 0

            if downloads < min_downloads:
                continue

            # Filter by size
            if size_limit_gb:
                size_str = model.get('size', '0')
                try:
                    if 'GB' in size_str:
                        size_gb = float(size_str.replace('GB', '').strip())
                    elif 'MB' in size_str:
                        size_gb = float(size_str.replace('MB', '').strip()) / 1000
                    else:
                        size_gb = 0

                    if size_gb > size_limit_gb:
                        continue
                except:
                    pass

            # Search in text fields
            if query_lower:
                searchable_text = " ".join([
                    model.get('name', ''),
                    model.get('description', ''),
                    model.get('pipeline_tag', ''),
                    " ".join(model.get('tags', [])),
                    model.get('model_name', '')
                ]).lower()

                if query_lower not in searchable_text:
                    continue

            # Filter by task
            if task:
                model_task = model.get('pipeline_tag', '')
                if task.lower() not in model_task.lower():
                    continue

            results.append(model)

        return results

    def get_model_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Znajdź model po nazwie"""
        if not self.combined_models:
            self.combine_models()

        for model in self.combined_models:
            if (model.get('name', '').lower() == name.lower() or
                    model.get('id', '').lower() == name.lower() or
                    model.get('model_name', '').lower() == name.lower()):
                return model
        return None

    def get_recommendations(self,
                            use_case: str = "general",
                            max_size_gb: float = 10.0,
                            min_downloads: int = 1000) -> List[Dict[str, Any]]:
        """Rekomendacje modeli dla konkretnych przypadków użycia"""

        use_case_filters = {
            "general": {
                "tasks": ["text-generation", "conversational"],
                "keywords": ["chat", "instruct", "general"]
            },
            "coding": {
                "tasks": ["text-generation"],
                "keywords": ["code", "coding", "programming", "starcoder", "codellama"]
            },
            "embedding": {
                "tasks": ["feature-extraction", "sentence-similarity"],
                "keywords": ["embed", "sentence", "similarity"]
            },
            "polish": {
                "tasks": ["text-generation", "conversational"],
                "keywords": ["polish", "polski", "bielik", "trurl"]
            },
            "small": {
                "max_size": 3.0,
                "tasks": ["text-generation"],
                "keywords": ["small", "mini", "tiny", "1b", "3b"]
            },
            "vision": {
                "tasks": ["image-to-text", "visual-question-answering"],
                "keywords": ["vision", "llava", "visual", "multimodal"]
            }
        }

        filters = use_case_filters.get(use_case, use_case_filters["general"])

        results = self.search_models(
            local_ready_only=True,
            min_downloads=min_downloads,
            size_limit_gb=min(max_size_gb, filters.get('max_size', max_size_gb))
        )

        # Score models based on use case
        scored_models = []
        for model in results:
            score = 0

            # Task match
            if model.get('pipeline_tag') in filters.get('tasks', []):
                score += 10

            # Keyword match
            model_text = " ".join([
                model.get('name', ''),
                model.get('description', ''),
                " ".join(model.get('tags', []))
            ]).lower()

            for keyword in filters.get('keywords', []):
                if keyword in model_text:
                    score += 5

            # Download popularity
            downloads = model.get('downloads', 0) or model.get('pulls', 0)
            if isinstance(downloads, str):
                try:
                    if 'M' in downloads:
                        downloads = float(downloads.replace('M', '')) * 1000000
                    elif 'k' in downloads or 'K' in downloads:
                        downloads = float(downloads.replace('k', '').replace('K', '')) * 1000
                except:
                    downloads = 0

            score += min(downloads / 100000, 10)  # Max 10 points for popularity

            # Local readiness bonus
            if model.get('local_ready'):
                score += 5

            if score > 0:
                model['recommendation_score'] = score
                scored_models.append(model)

        # Sort by score
        scored_models.sort(key=lambda x: x['recommendation_score'], reverse=True)
        return scored_models[:20]  # Top 20

    def generate_install_script(self, models: List[Dict[str, Any]],
                                output_file: str = "install_models.sh") -> str:
        """Generuje skrypt do instalacji modeli"""

        script_lines = [
            "#!/bin/bash",
            "# Auto-generated model installation script",
            f"# Generated on {datetime.now().isoformat()}",
            "",
            "echo '🚀 Installing selected AI models...'",
            ""
        ]

        ollama_models = []
        hf_models = []

        for model in models:
            if model['source'] == 'ollama':
                ollama_models.append(model)
            elif model.get('gguf_available'):
                hf_models.append(model)

        # Ollama models
        if ollama_models:
            script_lines.extend([
                "echo '📦 Installing Ollama models...'",
                ""
            ])

            for model in ollama_models:
                script_lines.append(f"echo 'Installing {model['name']}...'")
                script_lines.append(f"ollama pull {model['name']}")
                script_lines.append("")

        # HuggingFace GGUF models
        if hf_models:
            script_lines.extend([
                "echo '📦 HuggingFace GGUF models (manual download required):'",
                ""
            ])

            for model in hf_models:
                script_lines.append(f"echo 'Model: {model['name']}'")
                script_lines.append(f"echo 'URL: {model['url']}'")
                script_lines.append(f"echo 'Download GGUF files manually and import to Ollama'")
                script_lines.append("")

        script_lines.extend([
            "echo '✅ Model installation completed!'",
            "echo 'Run: ollama list' to see installed models"
        ])

        script_content = "\n".join(script_lines)

        try:
            with open(output_file, 'w') as f:
                f.write(script_content)

            # Make executable
            os.chmod(output_file, 0o755)
            print(f"💾 Installation script saved to {output_file}")

        except Exception as e:
            print(f"❌ Error saving script: {e}")

        return script_content

    def export_models(self, models: List[Dict[str, Any]],
                      output_file: str, format: str = "json"):
        """Eksportuje modele do różnych formatów"""

        if format == "json":
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "exported_at": datetime.now().isoformat(),
                        "total_models": len(models),
                        "models": models
                    }, f, indent=2, ensure_ascii=False)
                print(f"💾 Exported {len(models)} models to {output_file}")
            except Exception as e:
                print(f"❌ Error exporting JSON: {e}")

        elif format == "csv":
            try:
                import csv
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    if models:
                        fieldnames = models[0].keys()
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(models)
                print(f"💾 Exported {len(models)} models to {output_file}")
            except Exception as e:
                print(f"❌ Error exporting CSV: {e}")

        elif format == "md":
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"# AI Models Export\n\n")
                    f.write(f"Exported {len(models)} models on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                    for model in models:
                        f.write(f"## {model.get('name', 'Unknown')}\n\n")
                        f.write(f"- **Source**: {model.get('source', 'Unknown')}\n")
                        f.write(f"- **URL**: {model.get('url', 'N/A')}\n")
                        f.write(f"- **Downloads**: {model.get('downloads', 0)}\n")
                        f.write(f"- **Size**: {model.get('size', 'Unknown')}\n")
                        f.write(f"- **Task**: {model.get('pipeline_tag', 'Unknown')}\n")
                        f.write(f"- **Local Ready**: {'✅' if model.get('local_ready') else '❌'}\n")
                        if model.get('description'):
                            f.write(f"- **Description**: {model['description'][:200]}...\n")
                        f.write("\n")

                print(f"💾 Exported {len(models)} models to {output_file}")
            except Exception as e:
                print(f"❌ Error exporting Markdown: {e}")

    def print_summary(self):
        """Wyświetla podsumowanie dostępnych modeli"""
        if not self.combined_models:
            self.combine_models()

        total = len(self.combined_models)
        ollama_models = [m for m in self.combined_models if m['source'] == 'ollama']
        hf_models = [m for m in self.combined_models if m['source'] == 'huggingface']
        local_ready = [m for m in self.combined_models if m.get('local_ready', False)]

        print(f"\n📊 MODELS SUMMARY:")
        print(f"Total models: {total}")
        print(f"Ollama models: {len(ollama_models)}")
        print(f"HuggingFace models: {len(hf_models)}")
        print(f"Ready for local use: {len(local_ready)}")

        # Task distribution
        tasks = {}
        for model in self.combined_models:
            task = model.get('pipeline_tag', 'unknown')
            tasks[task] = tasks.get(task, 0) + 1

        print(f"\n📋 Top tasks:")
        for task, count in sorted(tasks.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {task}: {count}")


def main():
    parser = argparse.ArgumentParser(description='Unified Models Manager')
    parser.add_argument('--ollama-file', default='ollama_models.json',
                        help='Ollama models JSON file')
    parser.add_argument('--hf-file', default='huggingface_models.json',
                        help='HuggingFace models JSON file')
    parser.add_argument('--search', '-s', type=str,
                        help='Search models')
    parser.add_argument('--source', choices=['all', 'ollama', 'huggingface'],
                        default='all', help='Filter by source')
    parser.add_argument('--task', '-t', type=str,
                        help='Filter by task')
    parser.add_argument('--local-only', action='store_true',
                        help='Only show models ready for local use')
    parser.add_argument('--min-downloads', type=int, default=0,
                        help='Minimum downloads/pulls')
    parser.add_argument('--max-size', type=float,
                        help='Maximum size in GB')
    parser.add_argument('--recommend', choices=['general', 'coding', 'embedding',
                                                'polish', 'small', 'vision'],
                        help='Get recommendations for use case')
    parser.add_argument('--export', type=str,
                        help='Export results to file')
    parser.add_argument('--format', choices=['json', 'csv', 'md'],
                        default='json', help='Export format')
    parser.add_argument('--install-script', type=str,
                        help='Generate installation script')
    parser.add_argument('--limit', type=int, default=50,
                        help='Limit number of results')

    args = parser.parse_args()

    manager = UnifiedModelsManager()
    manager.load_data(args.ollama_file, args.hf_file)

    if args.recommend:
        # Recommendation mode
        models = manager.get_recommendations(
            use_case=args.recommend,
            max_size_gb=args.max_size or 10.0,
            min_downloads=args.min_downloads
        )

        print(f"\n🎯 RECOMMENDATIONS FOR '{args.recommend.upper()}':")
        for i, model in enumerate(models[:args.limit], 1):
            score = model.get('recommendation_score', 0)
            ready = "✅" if model.get('local_ready') else "❌"
            print(f"{i}. {model.get('name', 'Unknown')} {ready} (Score: {score:.1f})")
            print(f"   Source: {model['source']}, Task: {model.get('pipeline_tag', 'Unknown')}")
            print(f"   Downloads: {model.get('downloads', 0)}, Size: {model.get('size', 'Unknown')}")
            if model.get('description'):
                print(f"   {model['description'][:100]}...")
            print()

    elif args.search or args.task or args.source != 'all' or args.local_only:
        # Search mode
        models = manager.search_models(
            query=args.search or "",
            source=args.source,
            task=args.task or "",
            local_ready_only=args.local_only,
            min_downloads=args.min_downloads,
            size_limit_gb=args.max_size
        )

        print(f"\n🔍 SEARCH RESULTS ({len(models)} found):")
        for i, model in enumerate(models[:args.limit], 1):
            ready = "✅" if model.get('local_ready') else "❌"
            print(f"{i}. {model.get('name', 'Unknown')} {ready}")
            print(f"   Source: {model['source']}, Task: {model.get('pipeline_tag', 'Unknown')}")
            print(f"   Downloads: {model.get('downloads', 0)}, Size: {model.get('size', 'Unknown')}")
            print(f"   URL: {model.get('url', 'N/A')}")
            print()

        # Export if requested
        if args.export:
            manager.export_models(models[:args.limit], args.export, args.format)

        # Generate install script if requested
        if args.install_script:
            manager.generate_install_script(models[:args.limit], args.install_script)

    else:
        # Summary mode
        manager.print_summary()


if __name__ == "__main__":
    main()