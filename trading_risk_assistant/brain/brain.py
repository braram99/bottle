"""
Trading Risk Assistant - Brain/Coach
Mini coach que analiza patrones y da sugerencias motivacionales.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from journal import JournalManager
from risk_logic import ConfigLoader


class TradingCoach:
    """Coach inteligente que analiza tu comportamiento y da sugerencias."""
    
    def __init__(self, journal: JournalManager, config: ConfigLoader):
        self.journal = journal
        self.config = config
    
    def check_inactivity(self) -> Optional[str]:
        """
        Verifica si el trader ha estado inactivo mucho tiempo.
        
        Returns:
            Mensaje motivacional si hay inactividad, None si no
        """
        days_inactive = self.journal.days_since_last_trade()
        
        if days_inactive is None:
            return None
        
        warning_days = self.config.get('coach', 'days_inactive_warning', default=3)
        
        if days_inactive >= warning_days:
            messages = self.config.get('coach', 'motivational_messages', default=[])
            if messages:
                message = random.choice(messages)
                return message.format(days=days_inactive)
            else:
                return f"💪 Llevas {days_inactive} días sin operar. ¿Qué tal revisar el mercado?"
        
        return None
    
    def analyze_psychology_pattern(self) -> Optional[str]:
        """
        Analiza patrones en la psicología del trader.
        
        Returns:
            Sugerencia basada en patrones psicológicos
        """
        entries = self.journal.get_entries(limit=7)
        
        if len(entries) < 3:
            return None
        
        # Analizar scores de psicología
        psych_scores = []
        for entry in entries:
            for answer in entry.get('answers', {}).items():
                if answer[0] in ['mental_state', 'emotional_control']:
                    psych_scores.append(answer[1])
        
        if not psych_scores:
            return None
        
        avg_psych = sum(psych_scores) / len(psych_scores)
        
        if avg_psych < 3:
            return ("🧠 He notado que tu estado mental ha estado bajo últimamente. "
                   "Considera tomar un descanso o hablar con alguien.")
        elif avg_psych < 3.5:
            return ("⚠️ Tu psicología ha estado irregular. Tal vez necesitas "
                   "establecer una rutina más consistente antes de tradear.")
        
        return None
    
    def analyze_risk_taking_pattern(self) -> Optional[str]:
        """
        Analiza patrones en la toma de riesgo.
        
        Returns:
            Sugerencia basada en patrones de riesgo
        """
        entries = self.journal.get_entries(limit=10, traded_only=True)
        
        if len(entries) < 5:
            return None
        
        risk_3_count = sum(1 for e in entries if e.get('decision', {}).get('risk_percent') == 3)
        risk_percentage = (risk_3_count / len(entries)) * 100
        
        if risk_percentage > 80:
            return ("⚠️ Estás tomando 3% de riesgo en la mayoría de tus trades. "
                   "Asegúrate de que realmente tienes las confluencias necesarias.")
        elif risk_percentage < 20:
            return ("💡 Has sido muy conservador últimamente. ¿Estás siendo demasiado "
                   "estricto con tus criterios? A veces menos es más, pero también "
                   "necesitas tomar trades cuando las condiciones son buenas.")
        
        return None
    
    def analyze_score_trend(self) -> Optional[str]:
        """
        Analiza la tendencia de los scores.
        
        Returns:
            Sugerencia basada en la tendencia de scores
        """
        entries = self.journal.get_entries(limit=10)
        
        if len(entries) < 5:
            return None
        
        scores = [e.get('decision', {}).get('final_score', 0) for e in entries]
        
        # Calcular tendencia simple (últimos 3 vs primeros 3)
        recent_avg = sum(scores[-3:]) / 3
        old_avg = sum(scores[:3]) / 3
        
        if recent_avg < old_avg - 10:
            return ("📉 Tus scores han estado bajando. ¿Algo está afectando tu análisis? "
                   "Tal vez necesites revisar tu metodología o tomar un descanso.")
        elif recent_avg > old_avg + 10:
            return ("📈 ¡Tus scores están mejorando! Sigue así, parece que estás "
                   "refinando tu proceso de análisis.")
        
        return None
    
    def analyze_hard_stop_triggers(self) -> Optional[str]:
        """
        Analiza qué hard stops se están activando más frecuentemente.
        
        Returns:
            Sugerencia basada en hard stops activados
        """
        entries = self.journal.get_entries(limit=10)
        
        if len(entries) < 5:
            return None
        
        # Contar entradas donde no pasaron los hard stops
        failed_entries = [e for e in entries 
                         if not e.get('decision', {}).get('hard_stops_passed', True)]
        
        if len(failed_entries) > len(entries) * 0.3:  # Más del 30%
            return ("🛑 Estás fallando los hard stops con frecuencia. Esto es bueno - "
                   "el sistema te está protegiendo. Pero considera trabajar en las "
                   "áreas que más te están deteniendo.")
        
        return None
    
    def get_daily_motivation(self) -> str:
        """
        Genera un mensaje motivacional diario.
        
        Returns:
            Mensaje motivacional
        """
        motivations = [
            "🎯 Recuerda: La consistencia vence al talento cada vez.",
            "💪 Un día a la vez. Cada decisión cuenta.",
            "📊 No necesitas operar todos los días. Necesitas operar bien.",
            "🧠 Tu mejor trade es el que no tomas cuando las condiciones no están.",
            "✨ El trading es un maratón, no un sprint.",
            "🎓 Cada sesión es una oportunidad de aprender.",
            "🚀 Confía en tu proceso. Los resultados llegarán.",
            "🔍 La paciencia es la habilidad más rentable en trading.",
        ]
        
        return random.choice(motivations)
    
    def get_insights(self) -> Dict[str, Any]:
        """
        Genera un reporte completo de insights y sugerencias.
        
        Returns:
            Diccionario con todos los insights
        """
        insights = {
            'inactivity_warning': self.check_inactivity(),
            'psychology_insight': self.analyze_psychology_pattern(),
            'risk_taking_insight': self.analyze_risk_taking_pattern(),
            'score_trend_insight': self.analyze_score_trend(),
            'hard_stop_insight': self.analyze_hard_stop_triggers(),
            'daily_motivation': self.get_daily_motivation(),
            'generated_at': datetime.now().isoformat()
        }
        
        # Filtrar None values
        insights = {k: v for k, v in insights.items() if v is not None}
        
        return insights
    
    def print_coaching_message(self):
        """Imprime un mensaje de coaching en consola."""
        insights = self.get_insights()
        
        print("\n" + "="*60)
        print("🧠 MENSAJE DE TU COACH")
        print("="*60)
        
        # Siempre mostrar motivación diaria
        print(f"\n{insights.get('daily_motivation', '')}")
        
        # Mostrar insights relevantes
        has_insights = False
        
        if 'inactivity_warning' in insights:
            print(f"\n{insights['inactivity_warning']}")
            has_insights = True
        
        if 'psychology_insight' in insights:
            print(f"\n{insights['psychology_insight']}")
            has_insights = True
        
        if 'risk_taking_insight' in insights:
            print(f"\n{insights['risk_taking_insight']}")
            has_insights = True
        
        if 'score_trend_insight' in insights:
            print(f"\n{insights['score_trend_insight']}")
            has_insights = True
        
        if 'hard_stop_insight' in insights:
            print(f"\n{insights['hard_stop_insight']}")
            has_insights = True
        
        if not has_insights:
            print("\n✅ Todo se ve bien. Sigue con tu proceso y mantén la disciplina.")
        
        print("\n" + "="*60)
    
    def get_weekly_report(self) -> str:
        """
        Genera un reporte semanal del desempeño.
        
        Returns:
            Reporte formateado como string
        """
        stats = self.journal.get_stats(7)
        insights = self.get_insights()
        
        report = []
        report.append("="*60)
        report.append("📊 REPORTE SEMANAL")
        report.append("="*60)
        
        report.append(f"\n📈 Resumen:")
        report.append(f"   • Sesiones completadas: {stats['total_sessions']}")
        report.append(f"   • Trades tomados: {stats['trades_taken']}")
        report.append(f"   • Score promedio: {stats['avg_score']}/100")
        report.append(f"   • Tasa de operación: {stats['trade_rate']}%")
        
        report.append(f"\n🎯 Distribución de riesgo:")
        report.append(f"   • 2% riesgo: {stats['risk_2_percent_count']} trades")
        report.append(f"   • 3% riesgo: {stats['risk_3_percent_count']} trades")
        
        report.append(f"\n💡 Insights de tu coach:")
        
        insight_keys = ['psychology_insight', 'risk_taking_insight', 
                       'score_trend_insight', 'hard_stop_insight']
        
        for key in insight_keys:
            if key in insights:
                report.append(f"   • {insights[key]}")
        
        report.append(f"\n{insights.get('daily_motivation', '')}")
        report.append("="*60)
        
        return "\n".join(report)
