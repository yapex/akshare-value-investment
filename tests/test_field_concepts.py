#!/usr/bin/env python3
"""
字段概念映射系统测试
"""

import pytest
import tempfile
import os
from pathlib import Path
from typing import Dict, Any

# 导入待测试的模块
from akshare_value_investment.field_concepts.models import (
    ConceptSearchResult,
    MarketField,
    ConceptConfig,
)


class TestMarketField:
    """测试市场字段数据模型"""

    def test_market_field_creation_success(self):
        """测试市场字段创建成功"""
        field = MarketField(
            name="摊薄每股收益(元)",
            unit="元",
            priority=1,
            latest_value=5.23
        )

        assert field.name == "摊薄每股收益(元)"
        assert field.unit == "元"
        assert field.priority == 1
        assert field.latest_value == 5.23

    def test_market_field_to_dict(self):
        """测试市场字段转换为字典"""
        field = MarketField(
            name="BASIC_EPS",
            unit="港元",
            priority=1,
            latest_value=20.94
        )

        result = field.to_dict()
        expected = {
            "name": "BASIC_EPS",
            "unit": "港元",
            "priority": 1,
            "latest_value": 20.94
        }

        assert result == expected


class TestConceptSearchResult:
    """测试概念搜索结果数据模型"""

    def test_concept_search_result_creation(self):
        """测试概念搜索结果创建"""
        fields = {
            "a_stock": [
                MarketField(name="摊薄每股收益(元)", unit="元", priority=1)
            ],
            "hk_stock": [
                MarketField(name="BASIC_EPS", unit="港元", priority=1)
            ]
        }

        result = ConceptSearchResult(
            concept_id="eps",
            concept_name="每股收益",
            confidence=0.95,
            description="公司每股股票的盈利金额",
            available_fields=fields
        )

        assert result.concept_id == "eps"
        assert result.concept_name == "每股收益"
        assert result.confidence == 0.95
        assert result.description == "公司每股股票的盈利金额"
        assert "a_stock" in result.available_fields
        assert "hk_stock" in result.available_fields

    def test_concept_search_result_to_dict(self):
        """测试概念搜索结果转换为字典"""
        fields = {
            "a_stock": [
                MarketField(name="摊薄每股收益(元)", unit="元", priority=1)
            ]
        }

        result = ConceptSearchResult(
            concept_id="eps",
            concept_name="每股收益",
            confidence=0.95,
            description="公司每股股票的盈利金额",
            available_fields=fields
        )

        result_dict = result.to_dict()

        assert result_dict["concept_id"] == "eps"
        assert result_dict["concept_name"] == "每股收益"
        assert result_dict["confidence"] == 0.95
        assert result_dict["description"] == "公司每股股票的盈利金额"
        assert "a_stock" in result_dict["available_fields"]
        assert isinstance(result_dict["available_fields"]["a_stock"], list)


class TestConceptConfig:
    """测试概念配置数据模型"""

    def test_load_config_from_dict(self):
        """测试从字典加载配置"""
        config_dict = {
            "version": "1.0.0",
            "concepts": {
                "eps": {
                    "name": "每股收益",
                    "aliases": ["基本每股收益", "EPS"],
                    "keywords": ["每股", "收益", "EPS"],
                    "category": "盈利能力",
                    "importance": "高",
                    "description": "公司每股股票的盈利金额",
                    "market_mappings": {
                        "a_stock": {
                            "fields": [
                                {"name": "摊薄每股收益(元)", "unit": "元", "priority": 1}
                            ]
                        }
                    }
                }
            }
        }

        config = ConceptConfig.from_dict(config_dict)

        assert config.version == "1.0.0"
        assert "eps" in config.concepts
        assert config.concepts["eps"]["name"] == "每股收益"
        assert "基本每股收益" in config.concepts["eps"]["aliases"]
        assert "摊薄每股收益(元)" == config.concepts["eps"]["market_mappings"]["a_stock"]["fields"][0]["name"]

    def test_validate_config_success(self):
        """测试配置验证成功"""
        valid_config = {
            "version": "1.0.0",
            "concepts": {
                "eps": {
                    "name": "每股收益",
                    "market_mappings": {
                        "a_stock": {"fields": []}
                    }
                }
            }
        }

        # 应该不抛出异常
        ConceptConfig.validate_config(valid_config)

    def test_validate_config_missing_version(self):
        """测试配置验证缺少版本"""
        invalid_config = {
            "concepts": {
                "eps": {
                    "name": "每股收益",
                    "market_mappings": {"a_stock": {"fields": []}}
                }
            }
        }

        with pytest.raises(ValueError, match="配置文件缺少必需字段: version"):
            ConceptConfig.validate_config(invalid_config)

    def test_validate_config_missing_concepts(self):
        """测试配置验证缺少概念"""
        invalid_config = {
            "version": "1.0.0"
        }

        with pytest.raises(ValueError, match="配置文件缺少必需字段: concepts"):
            ConceptConfig.validate_config(invalid_config)

    def test_validate_config_concept_missing_mappings(self):
        """测试概念缺少市场映射"""
        invalid_config = {
            "version": "1.0.0",
            "concepts": {
                "eps": {
                    "name": "每股收益"
                    # 缺少 market_mappings
                }
            }
        }

        with pytest.raises(ValueError, match="概念 eps 缺少市场映射"):
            ConceptConfig.validate_config(invalid_config)


class TestConfigIntegration:
    """配置集成测试"""

    def test_yaml_config_loading(self):
        """测试YAML配置加载"""
        yaml_content = """
version: "1.0.0"
concepts:
  eps:
    name: "每股收益"
    aliases:
      - "基本每股收益"
      - "EPS"
    keywords:
      - "每股"
      - "收益"
      - "EPS"
    category: "盈利能力"
    importance: "高"
    description: "公司每股股票的盈利金额"
    market_mappings:
      a_stock:
        fields:
          - name: "摊薄每股收益(元)"
            unit: "元"
            priority: 1
      hk_stock:
        fields:
          - name: "BASIC_EPS"
            unit: "港元"
            priority: 1
"""

        # 创建临时YAML文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            from akshare_value_investment.field_concepts.config_manager import ConfigManager
            config_manager = ConfigManager(temp_path)
            config = config_manager.load_config()[1]

            # 验证加载的配置
            assert config["version"] == "1.0.0"
            assert "eps" in config["concepts"]
            assert config["concepts"]["eps"]["name"] == "每股收益"
            assert len(config["concepts"]["eps"]["aliases"]) == 2
            assert len(config["concepts"]["eps"]["market_mappings"]) == 2

        finally:
            # 清理临时文件
            os.unlink(temp_path)


class TestSearchEngine:
    """概念搜索引擎测试"""

    def test_search_concepts_basic(self):
        """测试基础概念搜索"""
        from akshare_value_investment.field_concepts.search_engine import ConceptSearchEngine
        from akshare_value_investment.field_concepts.config_manager import ConfigManager

        # 创建测试配置
        test_config = {
            "version": "1.0.0",
            "concepts": {
                "eps": {
                    "name": "每股收益",
                    "aliases": ["基本每股收益", "EPS"],
                    "keywords": ["每股", "收益", "EPS"],
                    "category": "盈利能力",
                    "market_mappings": {
                        "a_stock": {
                            "fields": [{"name": "摊薄每股收益(元)", "unit": "元", "priority": 1}]
                        }
                    }
                },
                "roe": {
                    "name": "净资产收益率",
                    "aliases": ["ROE"],
                    "keywords": ["净资产", "收益率", "ROE"],
                    "market_mappings": {
                        "a_stock": {
                            "fields": [{"name": "净资产收益率(%)", "unit": "%", "priority": 1}]
                        }
                    }
                }
            }
        }

        # 创建模拟配置管理器
        class MockConfigManager:
            def __init__(self, config):
                self.config = config

            def get_config(self):
                return self.config

            def get_concept(self, concept_id):
                return self.config.get("concepts", {}).get(concept_id)

        config_manager = MockConfigManager(test_config)
        search_engine = ConceptSearchEngine(config_manager)

        # 测试搜索
        results = search_engine.search_concepts("每股收益")

        assert len(results) >= 1
        assert results[0].concept_id == "eps"
        assert results[0].concept_name == "每股收益"
        assert results[0].confidence > 0.8

    def test_search_concepts_multiple_matches(self):
        """测试多匹配结果搜索"""
        from akshare_value_investment.field_concepts.search_engine import ConceptSearchEngine
        from akshare_value_investment.field_concepts.config_manager import ConfigManager

        # 使用真实的配置文件
        config_path = Path(__file__).parent.parent / "src" / "akshare_value_investment" / "field_concepts" / "financial_concepts.yaml"
        config_manager = ConfigManager(str(config_path))
        search_engine = ConceptSearchEngine(config_manager)

        # 测试通用查询，应该有多个匹配
        results = search_engine.search_concepts("收益率")

        assert len(results) >= 1
        # 应该包含ROE
        concept_ids = [r.concept_id for r in results]
        assert "roe" in concept_ids

    def test_real_config_search(self):
        """测试真实配置文件的搜索"""
        from akshare_value_investment.field_concepts.search_engine import ConceptSearchEngine
        from akshare_value_investment.field_concepts.config_manager import ConfigManager

        # 使用真实的配置文件
        config_path = Path(__file__).parent.parent / "src" / "akshare_value_investment" / "field_concepts" / "financial_concepts.yaml"
        config_manager = ConfigManager(str(config_path))
        search_engine = ConceptSearchEngine(config_manager)

        # 测试EPS搜索
        results = search_engine.search_concepts("每股收益")
        assert len(results) >= 1
        eps_result = results[0]
        assert eps_result.concept_id == "eps"
        assert "a_stock" in eps_result.available_fields
        assert "hk_stock" in eps_result.available_fields
        assert "us_stock" in eps_result.available_fields

        # 验证字段映射
        a_stock_fields = eps_result.available_fields["a_stock"]
        assert len(a_stock_fields) >= 1
        assert "摊薄每股收益(元)" in [f.name for f in a_stock_fields]


if __name__ == "__main__":
    pytest.main([__file__])