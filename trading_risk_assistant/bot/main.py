"""
Trading Risk Assistant - CLI Principal
Bot interactivo para evaluar decisiones de trading.
"""

import sys
from typing import Dict, Any
from risk_logic import RiskAssistant
from journal import JournalManager


class TradingCLI:
    """Interfaz de línea de comandos para el asistente de riesgo."""
    
    def __init__(self):
        self.assistant = RiskAssistant()
        self.journal = JournalManager()
        self.answers = {}
        self.stats = {
            'consecutive_losses': 0,
            'daily_loss_percent': 0
        }
    
    def clear_screen(self):
        """Limpia la pantalla (funciona en Windows y Unix)."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Imprime el header del bot."""
        print("\n" + "="*60)
        print("🤖 TRADING RISK ASSISTANT".center(60))
        print("Tu coach personal de riesgo".center(60))
        print("="*60 + "\n")
    
    def ask_yes_no(self, question: str) -> bool:
        """Hace una pregunta de sí/no."""
        while True:
            answer = input(f"{question} (s/n): ").strip().lower()
            if answer in ['s', 'si', 'sí', 'y', 'yes']:
                return True
            elif answer in ['n', 'no']:
                return False
            else:
                print("❌ Por favor responde 's' o 'n'")
    
    def ask_number(self, question: str, min_val: float, max_val: float) -> float:
        """Hace una pregunta numérica con validación."""
        while True:
            try:
                answer = float(input(f"{question} [{min_val}-{max_val}]: ").strip())
                if min_val <= answer <= max_val:
                    return answer
                else:
                    print(f"❌ El valor debe estar entre {min_val} y {max_val}")
            except ValueError:
                print("❌ Por favor ingresa un número válido")
    
    def ask_scale(self, question: str, min_val: int, max_val: int) -> int:
        """Hace una pregunta de escala."""
        return int(self.ask_number(question, min_val, max_val))
    
    def collect_stats(self):
        """Recopila estadísticas básicas del trader."""
        print("\n📊 ESTADÍSTICAS ACTUALES\n")
        
        self.stats['consecutive_losses'] = int(self.ask_number(
            "¿Cuántas pérdidas consecutivas llevas?", 0, 10
        ))
        
        self.stats['daily_loss_percent'] = self.ask_number(
            "¿Cuánto % de pérdida llevas hoy?", 0, 100
        )
    
    def collect_answers(self):
        """Recopila todas las respuestas del usuario."""
        questions = self.assistant.get_questions()
        
        # 1. PSICOLOGÍA
        print("\n🧠 EVALUACIÓN PSICOLÓGICA\n")
        for q in questions['psychology']:
            if q['type'] == 'scale':
                self.answers[q['id']] = self.ask_scale(
                    q['question'], q['min'], q['max']
                )
            elif q['type'] == 'number':
                self.answers[q['id']] = self.ask_number(
                    q['question'], q['min'], q['max']
                )
            else:
                self.answers[q['id']] = self.ask_yes_no(q['question'])
        
        # 2. CONDICIONES DE MERCADO
        print("\n📈 CONDICIONES DE MERCADO\n")
        for q in questions['market_conditions']:
            if q['type'] == 'scale':
                self.answers[q['id']] = self.ask_scale(
                    q['question'], q['min'], q['max']
                )
            elif q['type'] == 'boolean':
                self.answers[q['id']] = self.ask_yes_no(q['question'])
        
        # 3. CONFLUENCIAS TÉCNICAS
        print("\n🔍 CONFLUENCIAS TÉCNICAS\n")
        for q in questions['technical_confluence']:
            if q['type'] == 'scale':
                self.answers[q['id']] = self.ask_scale(
                    q['question'], q['min'], q['max']
                )
            elif q['type'] == 'boolean':
                self.answers[q['id']] = self.ask_yes_no(q['question'])
    
    def collect_trade_details(self) -> Dict[str, Any]:
        """Recopila detalles del trade si se va a operar."""
        print("\n💼 DETALLES DEL TRADE\n")
        
        balance = self.ask_number("Balance de tu cuenta (USD)", 1, 1000000)
        sl_pips = self.ask_number("Stop Loss en pips", 1, 500)
        
        pair = input("Par de divisas (ej: EURUSD): ").strip().upper()
        
        return {
            'balance': balance,
            'sl_pips': sl_pips,
            'pair': pair
        }
    
    def show_detailed_breakdown(self, decision):
        """Muestra un desglose detallado de los scores."""
        print("\n" + "="*60)
        print("📋 DESGLOSE DETALLADO")
        print("="*60)
        
        categories = {}
        for answer in decision.answers:
            if answer.category not in categories:
                categories[answer.category] = []
            categories[answer.category].append(answer)
        
        for category, answers in categories.items():
            print(f"\n📌 {category.replace('_', ' ').title()}")
            print("-" * 60)
            for ans in answers:
                status = "✅" if ans.normalized_score >= 70 else "⚠️" if ans.normalized_score >= 40 else "❌"
                print(f"  {status} {ans.question_text}")
                print(f"     Respuesta: {ans.answer} | Score: {ans.normalized_score:.1f}/100")
    
    def run(self):
        """Ejecuta el flujo principal del CLI."""
        self.clear_screen()
        self.print_header()
        
        print("👋 ¡Bienvenido! Vamos a evaluar si debes tradear hoy.\n")
        
        # 1. Recopilar estadísticas
        self.collect_stats()
        
        # 2. Recopilar respuestas
        self.collect_answers()
        
        # 3. Evaluar decisión inicial (sin detalles de trade)
        decision = self.assistant.evaluate(self.answers, self.stats)
        
        # 4. Mostrar decisión
        print("\n" + self.assistant.format_decision(decision))
        
        # 5. Mostrar desglose si el usuario quiere
        if self.ask_yes_no("\n¿Quieres ver el desglose detallado?"):
            self.show_detailed_breakdown(decision)
        
        # 6. Si puede tradear, calcular tamaño de lote
        lot_size = None
        trade_details = None
        
        if decision.should_trade:
            if self.ask_yes_no("\n¿Quieres calcular el tamaño de lote?"):
                trade_details = self.collect_trade_details()
                
                # Re-evaluar con detalles de trade
                decision = self.assistant.evaluate(
                    self.answers,
                    self.stats,
                    balance=trade_details['balance'],
                    sl_pips=trade_details['sl_pips'],
                    pair=trade_details['pair']
                )
                
                print(f"\n💰 Tamaño de lote calculado: {decision.lot_size} lotes")
                print(f"   Riesgo: {decision.risk_percent}% = ${trade_details['balance'] * decision.risk_percent / 100:.2f}")
        
        # 7. Guardar en journal
        if self.ask_yes_no("\n¿Quieres guardar esta sesión en el journal?"):
            notes = input("Notas adicionales (opcional): ").strip()
            
            entry_data = {
                'answers': self.answers,
                'stats': self.stats,
                'decision': {
                    'should_trade': decision.should_trade,
                    'risk_percent': decision.risk_percent,
                    'final_score': decision.final_score,
                    'category_scores': decision.category_scores,
                    'hard_stops_passed': decision.hard_stop_result.passed
                },
                'trade_details': trade_details,
                'lot_size': decision.lot_size,
                'notes': notes
            }
            
            self.journal.add_entry(entry_data)
            print("✅ Sesión guardada en el journal")
        
        print("\n" + "="*60)
        print("👋 ¡Que tengas un buen día de trading!")
        print("="*60 + "\n")


def main():
    """Punto de entrada principal."""
    try:
        cli = TradingCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
