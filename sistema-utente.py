import json
import os

FICHEIRO_DADOS = "utentes_db.json"


class Consulta:
    def __init__(self, id_consulta: int, data: str, medico: str, diagnostico: str, observacoes: str):
        self.id_consulta = id_consulta
        self.data = data
        self.medico = medico
        self.diagnostico = diagnostico
        self.observacoes = observacoes

    def to_dict(self):
        return {
            "id_consulta": self.id_consulta,
            "data": self.data,
            "medico": self.medico,
            "diagnostico": self.diagnostico,
            "observacoes": self.observacoes
        }

    @classmethod
    def from_dict(cls, dados: dict):
        return cls(
            dados["id_consulta"],
            dados["data"],
            dados["medico"],
            dados["diagnostico"],
            dados["observacoes"]
        )

    def __str__(self):
        return (f"    - [ID Consulta: {self.id_consulta}] Data: {self.data} | Médico: {self.medico}\n"
                f"      Diagnóstico: {self.diagnostico}\n"
                f"      Observações: {self.observacoes}")


class Utente:
    def __init__(self, numero_registo: str, nome: str, nif: str, data_nascimento: str, contacto: str,
                 historico_clinico=None, contador_consultas=1):
        self.numero_registo = numero_registo
        self.nome = nome
        self.nif = nif if nif else "Não atribuído"
        self.data_nascimento = data_nascimento
        self.contacto = contacto
        self.historico_clinico = historico_clinico if historico_clinico else []
        self.contador_consultas = contador_consultas

    def adicionar_consulta(self, data: str, medico: str, diagnostico: str, observacoes: str):
        consulta = Consulta(self.contador_consultas, data, medico, diagnostico, observacoes)
        self.historico_clinico.append(consulta)
        self.contador_consultas += 1
        return consulta.id_consulta

    def to_dict(self):
        return {
            "numero_registo": self.numero_registo,
            "nome": self.nome,
            "nif": self.nif,
            "data_nascimento": self.data_nascimento,
            "contacto": self.contacto,
            "contador_consultas": self.contador_consultas,
            "historico_clinico": [c.to_dict() for c in self.historico_clinico]
        }

    @classmethod
    def from_dict(cls, dados: dict):
        historico = [Consulta.from_dict(c) for c in dados.get("historico_clinico", [])]
        return cls(
            dados["numero_registo"],
            dados["nome"],
            dados["nif"],
            dados["data_nascimento"],
            dados["contacto"],
            historico,
            dados.get("contador_consultas", 1)
        )

    def __str__(self):
        return (f"Nº Registo: {self.numero_registo} | Nome: {self.nome} | "
                f"NIF: {self.nif} | Data Nasc.: {self.data_nascimento} | Contacto: {self.contacto}")


class SistemaSaude:
    def __init__(self):
        self.utentes = {}  # Dicionário: chave = numero_registo, valor = Utente
        self.contador_utentes = 1
        self.carregar_dados()

    def carregar_dados(self):
        """Carrega os utentes do ficheiro JSON, se existir."""
        if os.path.exists(FICHEIRO_DADOS):
            try:
                with open(FICHEIRO_DADOS, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    self.contador_utentes = dados.get("contador_utentes", 1)
                    for reg, u_dict in dados.get("utentes", {}).items():
                        self.utentes[reg] = Utente.from_dict(u_dict)
                print(f"[Sistema] Dados carregados com sucesso de {FICHEIRO_DADOS}.")
            except Exception as e:
                print(f"[Aviso] Erro ao carregar o ficheiro de dados: {e}")

    def guardar_dados(self):
        """Guarda todos os utentes num ficheiro JSON."""
        try:
            dados = {
                "contador_utentes": self.contador_utentes,
                "utentes": {reg: u.to_dict() for reg, u in self.utentes.items()}
            }
            with open(FICHEIRO_DADOS, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[Erro] Não foi possível guardar os dados: {e}")

    def registar_utente(self, nome: str, nif: str, data_nascimento: str, contacto: str):
        if not nome.strip() or not data_nascimento.strip() or not contacto.strip():
            print("\n[Erro] Os campos Nome, Data de Nascimento e Contacto são obrigatórios!")
            return None

        numero_registo = f"UT{self.contador_utentes:03d}"
        novo_utente = Utente(numero_registo, nome.strip(), nif.strip(), data_nascimento.strip(), contacto.strip())
        self.utentes[numero_registo] = novo_utente
        self.contador_utentes += 1
        self.guardar_dados()
        print(f"\n[Sucesso] Utente registado com o número: {numero_registo}")
        return numero_registo

    def listar_utentes(self):
        if not self.utentes:
            print("\n[Aviso] Nenhum utente registado no sistema.")
            return
        print("\n--- LISTA DE UTENTES REGISTADOS ---")
        for utente in self.utentes.values():
            print(utente)

    def pesquisar_utentes(self, termo: str):
        """Pesquisa utentes por número de registo, NIF ou parte do nome."""
        termo = termo.lower().strip()
        resultados = []
        for utente in self.utentes.values():
            if (termo in utente.numero_registo.lower() or
                    termo in utente.nif.lower() or
                    termo in utente.nome.lower()):
                resultados.append(utente)

        if not resultados:
            print(f"\n[Aviso] Nenhum utente encontrado com o termo '{termo}'.")
            return

        print(f"\n--- RESULTADOS DA PESQUISA ('{termo}') ---")
        for utente in resultados:
            print(utente)
            print("-" * 50)

    def consultar_ficha_completa(self, numero_registo: str):
        utente = self.utentes.get(numero_registo.upper().strip())
        if not utente:
            print(f"\n[Erro] Utente com o número '{numero_registo}' não encontrado.")
            return None

        print("\n================ FICHA CLÍNICA DO UTENTE ================")
        print(utente)
        print("-" * 57)
        print("Histórico Clínico e Consultas:")
        if not utente.historico_clinico:
            print("  (Sem registos clínicos anteriores)")
        else:
            for consulta in utente.historico_clinico:
                print(consulta)
                print("-" * 40)
        print("=========================================================")
        return utente

    def atualizar_utente(self, numero_registo: str, nome: str, nif: str, contacto: str):
        utente = self.utentes.get(numero_registo.upper().strip())
        if not utente:
            print(f"\n[Erro] Utente '{numero_registo}' não encontrado.")
            return False

        if nome.strip(): utente.nome = nome.strip()
        if nif.strip(): utente.nif = nif.strip()
        if contacto.strip(): utente.contacto = contacto.strip()

        self.guardar_dados()
        print(f"\n[Sucesso] Dados do utente {numero_registo} atualizados com sucesso!")
        return True

    def remover_utente(self, numero_registo: str):
        reg = numero_registo.upper().strip()
        if reg in self.utentes:
            del self.utentes[reg]
            self.guardar_dados()
            print(f"\n[Sucesso] Utente {reg} removido do sistema.")
            return True
        print(f"\n[Erro] Utente '{reg}' não encontrado.")
        return False

    def adicionar_consulta_utente(self, numero_registo: str, data: str, medico: str, diagnostico: str,
                                  observacoes: str):
        utente = self.utentes.get(numero_registo.upper().strip())
        if not utente:
            print(f"\n[Erro] Utente '{numero_registo}' não encontrado.")
            return False

        if not data.strip() or not medico.strip() or not diagnostico.strip():
            print("\n[Erro] Data, Médico e Diagnóstico são campos obrigatórios para a consulta.")
            return False

        id_cons = utente.adicionar_consulta(data.strip(), medico.strip(), diagnostico.strip(), observacoes.strip())
        self.guardar_dados()
        print(f"\n[Sucesso] Consulta ID {id_cons} adicionada ao histórico do utente {numero_registo}.")
        return True


# --- INTERFACES POR NÍVEIS DE ACESSO (PERFIS) ---

def menu_recepcao(sistema: SistemaSaude):
    while True:
        print("\n--- MENU: RECEÇÃO / ADMINISTRADOR ---")
        print("1. Registar Novo Utente")
        print("2. Listar Todos os Utentes")
        print("3. Pesquisar Utente (por Nome, NIF ou Nº)")
        print("4. Atualizar Dados Cadastrais")
        print("5. Remover Utente")
        print("0. Terminar Sessão")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            nome = input("Nome completo: ")
            nif = input("Número de Identificação Fiscal (NIF) [Opcional]: ")
            data_nasc = input("Data de Nascimento (DD/MM/AAAA): ")
            contacto = input("Contacto telefónico: ")
            sistema.registar_utente(nome, nif, data_nasc, contacto)

        elif opcao == "2":
            sistema.listar_utentes()

        elif opcao == "3":
            termo = input("Insira o termo de pesquisa (Nome, NIF ou Nº Registo): ")
            sistema.pesquisar_utentes(termo)

        elif opcao == "4":
            registo = input("Número de Registo do utente a atualizar (ex: UT001): ")
            print("Deixe em branco caso não queira alterar o campo:")
            nome = input("Novo nome: ")
            nif = input("Novo NIF: ")
            contacto = input("Novo contacto: ")
            sistema.atualizar_utente(registo, nome, nif, contacto)

        elif opcao == "5":
            registo = input("Número de Registo do utente a remover: ")
            confirmacao = input(f"Tem certeza que deseja apagar o utente {registo}? (s/n): ").lower()
            if confirmacao == 's':
                sistema.remover_utente(registo)

        elif opcao == "0":
            print("\n[Sessão terminada] A voltar ao menu principal...")
            break
        else:
            print("\n[Erro] Opção inválida.")


def menu_medico(sistema: SistemaSaude):
    while True:
        print("\n--- MENU: PROFISSIONAL DE SAÚDE (MÉDICO) ---")
        print("1. Consultar Ficha e Histórico Clínico de Utente")
        print("2. Pesquisar Utente (por Nome, NIF ou Nº)")
        print("3. Registar Nova Consulta / Diagnóstico")
        print("0. Terminar Sessão")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            registo = input("Insira o Número de Registo do Utente (ex: UT001): ")
            sistema.consultar_ficha_completa(registo)

        elif opcao == "2":
            termo = input("Insira o termo de pesquisa (Nome, NIF ou Nº Registo): ")
            sistema.pesquisar_utentes(termo)

        elif opcao == "3":
            registo = input("Número de Registo do utente: ")
            data = input("Data da consulta (DD/MM/AAAA): ")
            medico = input("Nome do médico responsável: ")
            diagnostico = input("Diagnóstico clínico: ")
            obs = input("Observações e prescrições: ")
            sistema.adicionar_consulta_utente(registo, data, medico, diagnostico, obs)

        elif opcao == "0":
            print("\n[Sessão terminada] A voltar ao menu principal...")
            break
        else:
            print("\n[Erro] Opção inválida.")


def main():
    sistema = SistemaSaude()

    while True:
        print("\n=======================================================")
        print(" SISTEMA DE REGISTO ELETRÓNICO DE UTENTES - MINISTÉRIO DA SAÚDE")
        print("=======================================================")
        print(" Selecione o seu Perfil de Acesso:")
        print(" 1. Receção / Administrativo")
        print(" 2. Profissional de Saúde (Médico)")
        print(" 0. Sair da Aplicação")

        perfil = input("\nEscolha o perfil: ").strip()

        if perfil == "1":
            menu_recepcao(sistema)
        elif perfil == "2":
            menu_medico(sistema)
        elif perfil == "0":
            print("\n[Sistema] A encerrar a aplicação. Até breve!")
            break
        else:
            print("\n[Erro] Perfil inválido. Tente novamente.")


if __name__ == "__main__":
    main()