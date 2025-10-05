"""
Trading Risk Assistant - Lógica de Evaluación de Riesgo
Sistema modular para evaluar si operar y con cuánto riesgo.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import yaml
import json
from pathlib import Path


@dataclass
class Answer:
    """Representa una respuesta del usuario a una pregunta."""
    question_id: str
    question_text: str
    answer: Any
    category: str
    weight: float
    normalized_score: float = 0.0


@dataclass
class HardStopResult:
    """Resultado de la evaluación de hard stops."""
    passed: bool
    failed_checks: List[str] = field(default_factory=list)
    reason: Optional[str] = None


@dataclass
class RiskDecision:
    """Decisión final del sistema de riesgo."""
    should_trade: bool
    risk_percent: float
    final_score: float
    category_scores: Dict[str, float]
    answers: List[Answer]
    hard_stop_result: HardStopResult
    lot_size: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ConfigLoader:
    """Carga y valida la configuración desde config.yaml"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Carga el archivo de configuración."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get(self, *keys: str, default=None):
        """Obtiene un valor anidado de la configuración."""
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value


class HardStopEvaluator:
    """Evalúa las condiciones de hard stops que previenen el trading."""
    
    def __init__(self, config: ConfigLoader):
        self.config = config
    
    def evaluate(self, answers: Dict[str, Any], stats: Dict[str, Any]) -> HardStopResult:
        """
        Evalúa todos los hard stops.
        
        Args:
            answers: Diccionario con las respuestas del usuario
            stats: Estadísticas del trading (pérdidas consecutivas, etc.)
        
        Returns:
            HardStopResult con el resultado de la evaluación
        """
        failed_checks = []
        
        # 1. Verificar pérdidas consecutivas
        max_losses = self.config.get('hard_stops', 'max_consecutive_losses')
        if stats.get('consecutive_losses', 0) >= max_losses:
            failed_checks.append(f"Pérdidas consecutivas ({stats['consecutive_losses']}) >= {max_losses}")
        
        # 2. Verificar pérdida diaria
        max_daily_loss = self.config.get('hard_stops', 'max_daily_loss_percent')
        if stats.get('daily_loss_percent', 0) >= max_daily_loss:
            failed_checks.append(f"Pérdida diaria ({stats['daily_loss_percent']}%) >= {max_daily_loss}%")
        
        # 3. Verificar horas de sueño
        min_sleep = self.config.get('hard_stops', 'min_sleep_hours')
        sleep_hours = answers.get('sleep_quality', 0)
        if sleep_hours < min_sleep:
            failed_checks.append(f"Horas de sueño ({sleep_hours}) < {min_sleep}")
        
        # 4. Verificar score de psicología
        min_psych_score = self.config.get('hard_stops', 'psychology_min_score')
        mental_state = answers.get('mental_state', 0)
        if mental_state < min_psych_score:
            failed_checks.append(f"Estado mental ({mental_state}) < {min_psych_score}")
        
        # 5. Verificar bias claro
        require_bias = self.config.get('hard_stops', 'require_clear_bias')
        if require_bias and not answers.get('clear_bias', False):
            failed_checks.append("No tienes un bias claro del mercado")
        
        passed = len(failed_checks) == 0
        reason = None if passed else "Hard stops fallados: " + "; ".join(failed_checks)
        
        return HardStopResult(passed=passed, failed_checks=failed_checks, reason=reason)


class ScoreCalculator:
    """Calcula el score final basado en las respuestas del usuario."""
    
    def __init__(self, config: ConfigLoader):
        self.config = config
    
    def normalize_answer(self, question: Dict[str, Any], answer: Any) -> float:
        """
        Normaliza una respuesta a un score de 0-100.
        
        Args:
            question: Configuración de la pregunta
            answer: Respuesta del usuario
        
        Returns:
            Score normalizado (0-100)
        """
        q_type = question.get('type', 'boolean')
        
        if q_type == 'boolean':
            # Boolean: True = 100, False = 0
            base_score = 100 if answer else 0
            # Si reverse_score está activo, invertir
            if question.get('reverse_score', False):
                base_score = 100 - base_score
            return base_score
        
        elif q_type == 'scale':
            # Scale: normalizar entre min y max
            min_val = question.get('min', 1)
            max_val = question.get('max', 5)
            normalized = ((answer - min_val) / (max_val - min_val)) * 100
            return max(0, min(100, normalized))
        
        elif q_type == 'number':
            # Number: para horas de sueño, 8+ es perfecto
            if question['id'] == 'sleep_quality':
                if answer >= 8:
                    return 100
                elif answer >= 6:
                    return 70
                elif answer >= 5:
                    return 50
                else:
                    return 0
            return 0
        
        return 0
    
    def calculate_category_score(self, category: str, answers: Dict[str, Any]) -> Tuple[float, List[Answer]]:
        """
        Calcula el score de una categoría específica.
        
        Args:
            category: Nombre de la categoría (psychology, market_conditions, etc.)
            answers: Respuestas del usuario
        
        Returns:
            Tuple con (score_de_la_categoria, lista_de_objetos_Answer)
        """
        questions = self.config.get('questions', category, default=[])
        category_answers = []
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for question in questions:
            q_id = question['id']
            if q_id not in answers:
                continue
            
            answer_value = answers[q_id]
            normalized = self.normalize_answer(question, answer_value)
            weight = question.get('weight', 1.0)
            
            answer_obj = Answer(
                question_id=q_id,
                question_text=question['question'],
                answer=answer_value,
                category=category,
                weight=weight,
                normalized_score=normalized
            )
            category_answers.append(answer_obj)
            
            total_weighted_score += normalized * weight
            total_weight += weight
        
        category_score = total_weighted_score / total_weight if total_weight > 0 else 0
        return category_score, category_answers
    
    def calculate_final_score(self, answers: Dict[str, Any]) -> Tuple[float, Dict[str, float], List[Answer]]:
        """
        Calcula el score final ponderado de todas las categorías.
        
        Args:
            answers: Todas las respuestas del usuario
        
        Returns:
            Tuple con (score_final, scores_por_categoria, lista_completa_de_answers)
        """
        categories = ['psychology', 'market_conditions', 'technical_confluence']
        weights = self.config.get('scoring', 'weights', default={})
        
        category_scores = {}
        all_answers = []
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for category in categories:
            cat_score, cat_answers = self.calculate_category_score(category, answers)
            category_scores[category] = cat_score
            all_answers.extend(cat_answers)
            
            cat_weight = weights.get(category, 0)
            total_weighted_score += cat_score * cat_weight
            total_weight += cat_weight
        
        final_score = total_weighted_score / total_weight if total_weight > 0 else 0
        return final_score, category_scores, all_answers


class RiskDecisionMaker:
    """Toma la decisión final de riesgo basada en el score."""
    
    def __init__(self, config: ConfigLoader):
        self.config = config
    
    def decide_risk(self, final_score: float) -> Tuple[bool, float]:
        """
        Decide si operar y con qué porcentaje de riesgo.
        
        Args:
            final_score: Score final calculado (0-100)
        
        Returns:
            Tuple con (should_trade, risk_percent)
        """
        thresholds = self.config.get('scoring', 'thresholds', default={})
        no_trade = thresholds.get('no_trade', 50)
        risk_2 = thresholds.get('risk_2_percent', 70)
        
        if final_score < no_trade:
            return False, 0.0
        elif final_score < risk_2:
            return True, 2.0
        else:
            return True, 3.0
    
    def calculate_lot_size(
        self,
        risk_percent: float,
        balance: float,
        sl_pips: float,
        pair: str
    ) -> float:
        """
        Calcula el tamaño de lote basado en el riesgo.
        
        Args:
            risk_percent: Porcentaje de riesgo (2 o 3)
            balance: Balance de la cuenta
            sl_pips: Stop loss en pips
            pair: Par de divisas (ej: EURUSD)
        
        Returns:
            Tamaño de lote calculado
        """
        pip_values = self.config.get('lot_calculation', 'pip_values', default={})
        pip_value = pip_values.get(pair.upper(), 10)  # Default 10 USD por pip
        
        risk_amount = balance * (risk_percent / 100)
        lot_size = risk_amount / (sl_pips * pip_value)
        
        min_lot = self.config.get('lot_calculation', 'min_lot_size', default=0.01)
        max_lot = self.config.get('lot_calculation', 'max_lot_size', default=10.0)
        
        lot_size = max(min_lot, min(max_lot, lot_size))
        lot_size = round(lot_size, 2)
        
        return lot_size


class RiskAssistant:
    """Clase principal que orquesta todo el sistema de riesgo."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = ConfigLoader(config_path)
        self.hard_stop_evaluator = HardStopEvaluator(self.config)
        self.score_calculator = ScoreCalculator(self.config)
        self.decision_maker = RiskDecisionMaker(self.config)
    
    def evaluate(
        self,
        answers: Dict[str, Any],
        stats: Dict[str, Any],
        balance: Optional[float] = None,
        sl_pips: Optional[float] = None,
        pair: Optional[str] = None
    ) -> RiskDecision:
        """
        Evalúa todas las condiciones y toma una decisión de riesgo.
        
        Args:
            answers: Respuestas del usuario a todas las preguntas
            stats: Estadísticas del trading (pérdidas consecutivas, etc.)
            balance: Balance de la cuenta (opcional)
            sl_pips: Stop loss en pips (opcional)
            pair: Par de divisas (opcional)
        
        Returns:
            RiskDecision con toda la información de la decisión
        """
        # 1. Evaluar hard stops
        hard_stop_result = self.hard_stop_evaluator.evaluate(answers, stats)
        
        if not hard_stop_result.passed:
            return RiskDecision(
                should_trade=False,
                risk_percent=0.0,
                final_score=0.0,
                category_scores={},
                answers=[],
                hard_stop_result=hard_stop_result
            )
        
        # 2. Calcular score
        final_score, category_scores, all_answers = self.score_calculator.calculate_final_score(answers)
        
        # 3. Decidir riesgo
        should_trade, risk_percent = self.decision_maker.decide_risk(final_score)
        
        # 4. Calcular tamaño de lote si es necesario
        lot_size = None
        if should_trade and balance and sl_pips and pair:
            lot_size = self.decision_maker.calculate_lot_size(
                risk_percent, balance, sl_pips, pair
            )
        
        return RiskDecision(
            should_trade=should_trade,
            risk_percent=risk_percent,
            final_score=final_score,
            category_scores=category_scores,
            answers=all_answers,
            hard_stop_result=hard_stop_result,
            lot_size=lot_size
        )
    
    def get_questions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Retorna todas las preguntas organizadas por categoría."""
        return {
            'psychology': self.config.get('questions', 'psychology', default=[]),
            'market_conditions': self.config.get('questions', 'market_conditions', default=[]),
            'technical_confluence': self.config.get('questions', 'technical_confluence', default=[])
        }
    
    def format_decision(self, decision: RiskDecision) -> str:
        """
        Formatea la decisión en un texto legible.
        
        Args:
            decision: Decisión de riesgo
        
        Returns:
            String formateado con la decisión
        """
        output = []
        output.append("=" * 60)
        output.append("🎯 DECISIÓN DE TRADING")
        output.append("=" * 60)
        
        if not decision.hard_stop_result.passed:
            output.append("\n❌ NO PUEDES TRADEAR HOY")
            output.append(f"\n🛑 Razón: {decision.hard_stop_result.reason}")
            return "\n".join(output)
        
        output.append(f"\n📊 Score Final: {decision.final_score:.1f}/100")
        output.append("\n📈 Scores por Categoría:")
        for cat, score in decision.category_scores.items():
            output.append(f"  • {cat.replace('_', ' ').title()}: {score:.1f}/100")
        
        output.append(f"\n{'='*60}")
        
        if decision.should_trade:
            output.append(f"✅ PUEDES TRADEAR con {decision.risk_percent}% de riesgo")
            if decision.lot_size:
                output.append(f"💰 Tamaño de lote recomendado: {decision.lot_size} lotes")
        else:
            output.append("❌ NO OPERES HOY")
            output.append("   El score es demasiado bajo. Espera mejores condiciones.")
        
        output.append("=" * 60)
        
        return "\n".join(output)
