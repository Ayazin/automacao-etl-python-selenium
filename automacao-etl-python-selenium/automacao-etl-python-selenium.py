# -*- coding: utf-8 -*-
"""
Created on Thu Aug  7 16:19:36 2025

@author: gerson.silva
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
import time
import os


def run_test(path):

    # ============================================================
    # CONFIGURA SELENIUM
    # ============================================================

    options = Options()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)

    wait = WebDriverWait(
        driver,
        15
    )

    base_url = "https://smv.fde.sp.gov.br:8443"


    try:

        # ========================================================
        # LOGIN
        # ========================================================

        driver.get(
            base_url + "/index.action"
        )


        wait.until(
            EC.presence_of_element_located(
                (
                    By.NAME,
                    "iss_username"
                )
            )
        ).send_keys(
            "********"
        )


        wait.until(
            EC.presence_of_element_located(
                (
                    By.NAME,
                    "iss_password"
                )
            )
        ).send_keys(
            "*********" + Keys.RETURN
        )


        # ========================================================
        # ACESSA CONTRATOS
        # ========================================================

        wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//input[@value='Buscar Contrato(s)']"
                )
            )
        ).click()


        wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//td/a[starts-with(@href, "
                    "'/fornecedor/detalheContrato.action')]"
                )
            )
        )


        # ========================================================
        # COLETA LINKS DOS CONTRATOS
        # ========================================================

        itens = driver.find_elements(
            By.XPATH,
            "//td/a[starts-with(@href, "
            "'/fornecedor/detalheContrato.action')]"
        )


        contratos = []


        for item in itens:

            href = item.get_attribute(
                "href"
            )

            contrato_texto = (
                item.text.strip()
            )


            linha = item.find_element(
                By.XPATH,
                "./ancestor::tr"
            )


            tds = linha.find_elements(
                By.TAG_NAME,
                "td"
            )


            municipio = (
                tds[4].text.strip()
                if len(tds) > 4
                else ""
            )


            contratos.append(
                {
                    "contrato": contrato_texto,
                    "municipio": municipio,
                    "url": href
                }
            )


        print(
            f"\n✅ {len(contratos)} contratos encontrados."
        )


        # ========================================================
        # LISTAS PARA CONSOLIDAÇÃO
        # ========================================================

        dados_contratos = []

        dados_medicoes_merged = []


        # ========================================================
        # FUNÇÃO PARA EXTRAIR TABELA
        # USANDO SOMENTE SELENIUM
        # ========================================================

        def extrair_tabela(xpath_tabela):

            try:

                tabela_el = wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            xpath_tabela
                        )
                    )
                )


                # ------------------------------------------------
                # CABEÇALHOS
                # ------------------------------------------------

                cabecalhos = tabela_el.find_elements(
                    By.CSS_SELECTOR,
                    "thead tr th"
                )


                colunas = [
                    th.text.strip()
                    for th in cabecalhos
                ]


                # ------------------------------------------------
                # LINHAS
                # ------------------------------------------------

                linhas = tabela_el.find_elements(
                    By.CSS_SELECTOR,
                    "tbody tr"
                )


                dados = []


                for linha in linhas:

                    celulas = linha.find_elements(
                        By.CSS_SELECTOR,
                        "td"
                    )


                    valores = [
                        celula.text.strip()
                        for celula in celulas
                    ]


                    if valores:

                        dados.append(
                            valores
                        )


                # ------------------------------------------------
                # CASO NÃO TENHA LINHAS
                # ------------------------------------------------

                if not dados:

                    return pd.DataFrame(
                        columns=colunas
                    )


                # ------------------------------------------------
                # AJUSTA QUANTIDADE DE COLUNAS
                # ------------------------------------------------

                quantidade_colunas = (
                    len(colunas)
                )


                dados_ajustados = []


                for linha in dados:

                    if (
                        len(linha)
                        < quantidade_colunas
                    ):

                        linha = (
                            linha
                            + (
                                [""]
                                * (
                                    quantidade_colunas
                                    - len(linha)
                                )
                            )
                        )


                    elif (
                        len(linha)
                        > quantidade_colunas
                    ):

                        linha = (
                            linha[
                                :quantidade_colunas
                            ]
                        )


                    dados_ajustados.append(
                        linha
                    )


                # ------------------------------------------------
                # DATAFRAME
                # ------------------------------------------------

                df = pd.DataFrame(
                    dados_ajustados,
                    columns=colunas
                )


                return df


            except Exception as e:

                print(
                    f"⚠️ Erro ao extrair tabela: {e}"
                )

                return None


        # ========================================================
        # FUNÇÃO PARA EXTRAIR MEDIÇÕES
        # ========================================================

        def extrair_medicoes(
            xpath_tabela,
            sufixo="",
            xpath_final_coluna=None
        ):

            try:

                df = extrair_tabela(
                    xpath_tabela
                )


                if (
                    df is None
                    or df.empty
                ):

                    return None


                # ------------------------------------------------
                # GARANTE COLUNA FINAL
                # ------------------------------------------------

                if "Final" not in df.columns:

                    df["Final"] = ""


                # ------------------------------------------------
                # CASO EXISTA X EM ELEMENTO ESPECÍFICO
                # ------------------------------------------------

                if (
                    xpath_final_coluna
                    is not None
                ):

                    try:

                        elemento_x = wait.until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    xpath_final_coluna
                                )
                            )
                        )


                        valor_x = (
                            elemento_x.text.strip()
                        )


                        if len(df) > 0:

                            df.loc[
                                0,
                                "Final"
                            ] = valor_x


                    except Exception:

                        pass


                # ------------------------------------------------
                # MAPA DE COLUNAS
                # ------------------------------------------------

                col_map = {

                    "Medição":
                        "Medição" + sufixo,

                    "Data Ref.":
                        "Data Ref." + sufixo,

                    "Situação":
                        "Situação" + sufixo,

                    "Valor Prin.":
                        "Valor Prin." + sufixo,

                    "Valor Principal":
                        "Valor Prin." + sufixo,

                    "Final":
                        "Final" + sufixo
                }


                # ------------------------------------------------
                # PEGA SOMENTE COLUNAS NECESSÁRIAS
                # ------------------------------------------------

                colunas_presentes = [
                    col
                    for col in df.columns
                    if col in col_map
                ]


                df = df[
                    colunas_presentes
                ].copy()


                # ------------------------------------------------
                # RENOMEIA
                # ------------------------------------------------

                df.rename(
                    columns=col_map,
                    inplace=True
                )


                return df


            except Exception as e:

                print(
                    f"⚠️ Erro ao extrair medições: {e}"
                )

                return None


        # ========================================================
        # ITERA CADA CONTRATO
        # ========================================================

        for contrato in contratos:

            print(
                f"\n▶️ Acessando contrato: "
                f"{contrato['contrato']}"
            )


            try:

                # ==================================================
                # ABRE CONTRATO
                # ==================================================

                driver.get(
                    contrato["url"]
                )


                time.sleep(2)


                # ==================================================
                # TABELA 1 - MEDIÇÕES PRINCIPAL
                # ==================================================

                xpath_t2 = (
                    '//*[@id="main_left_content"]'
                    '//table[contains(@class,"results")]'
                )


                # ==================================================
                # EXTRAI TABELA 1 PARA VERIFICAÇÃO
                # ==================================================

                df_verificacao = extrair_tabela(
                    xpath_t2
                )


                if (
                    df_verificacao is None
                    or df_verificacao.empty
                ):

                    print(
                        "⚠️ Tabela 1 de medições "
                        "não encontrada."
                    )

                    continue


                # ==================================================
                # VERIFICA X + APROVADA
                #
                # SOMENTE NA TABELA 1
                # ==================================================

                if "Final" not in df_verificacao.columns:

                    df_verificacao["Final"] = ""


                if "Situação" not in df_verificacao.columns:

                    print(
                        "⚠️ Coluna Situação "
                        "não encontrada."
                    )

                    continue


                df_verificacao["Final"] = (
                    df_verificacao["Final"]
                    .astype(str)
                    .str.strip()
                    .str.upper()
                )


                df_verificacao["Situação"] = (
                    df_verificacao["Situação"]
                    .astype(str)
                    .str.strip()
                    .str.upper()
                )


                # ------------------------------------------------
                # FILTRA FINAL = X
                # ------------------------------------------------

                linhas_com_x = (
                    df_verificacao[
                        df_verificacao["Final"]
                        == "X"
                    ]
                )


                # ------------------------------------------------
                # VERIFICA X + APROVADA
                # ------------------------------------------------

                if not linhas_com_x.empty:

                    if (
                        linhas_com_x["Situação"]
                        == "APROVADA"
                    ).any():

                        print(
                            "❌ Medição com 'X' "
                            "e 'Aprovada' detectada."
                        )

                        print(
                            "   ↳ Pulando contrato."
                        )

                        continue


                print(
                    "✅ Validação X + Aprovada OK."
                )


                # ==================================================
                # EXTRAI TABELA PRINCIPAL DO CONTRATO
                # ==================================================

                dados_linha = {}


                try:

                    tabela = WebDriverWait(
                        driver,
                        20
                    ).until(
                        EC.presence_of_element_located(
                            (
                                By.CSS_SELECTOR,
                                ".selector > table"
                            )
                        )
                    )


                    linhas = tabela.find_elements(
                        By.TAG_NAME,
                        "tr"
                    )


                    for linha in linhas:

                        colunas = (
                            linha.find_elements(
                                By.TAG_NAME,
                                "td"
                            )
                        )


                        if len(colunas) == 2:

                            chave = (
                                colunas[0]
                                .text
                                .strip()
                                .replace(
                                    ":",
                                    ""
                                )
                            )


                            valor = (
                                colunas[1]
                                .text
                                .strip()
                            )


                            dados_linha[
                                chave
                            ] = valor


                except Exception as e:

                    print(
                        "⚠️ Erro ao extrair "
                        "tabela principal:",
                        e
                    )


                # ------------------------------------------------
                # ADICIONA IDENTIFICAÇÃO
                # ------------------------------------------------

                dados_linha["contrato"] = (
                    contrato["contrato"]
                )


                dados_linha["municipio"] = (
                    contrato["municipio"]
                )


                dados_contratos.append(
                    dados_linha
                )


                # ==================================================
                # EXTRAI TABELA 1
                # ==================================================

                df_t2 = extrair_medicoes(
                    xpath_t2
                )


                if (
                    df_t2 is None
                    or df_t2.empty
                ):

                    print(
                        "⚠️ Tabela 1 de medições "
                        "não encontrada."
                    )

                    continue


                print(
                    f"✅ Tabela 1 encontrada: "
                    f"{len(df_t2)} linhas."
                )


                # ==================================================
                # TABELA 2
                #
                # APENAS EXTRAI
                #
                # NÃO VERIFICA X
                # NÃO CLICA
                # ==================================================

                xpath_t3 = (
                    '//*[@id="main_left_content"]'
                    '/div[3]/div[2]/table'
                )


                df_t3 = extrair_medicoes(
                    xpath_t3,
                    " T3"
                )


                if (
                    df_t3 is None
                    or df_t3.empty
                ):

                    print(
                        "⚠️ Tabela 2 não encontrada."
                    )

                    df_t3 = None

                else:

                    print(
                        f"✅ Tabela 2 encontrada: "
                        f"{len(df_t3)} linhas."
                    )


                # ==================================================
                # TABELA 4
                #
                # CLICA NA MAIOR MEDIÇÃO DA TABELA 1
                # ==================================================

                df_tab4 = None


                try:

                    # ----------------------------------------------
                    # PEGA NÚMEROS DAS MEDIÇÕES
                    # ----------------------------------------------

                    medicoes_t2_numeros = (
                        df_t2["Medição"]
                        .astype(str)
                        .str.extract(
                            r"(\d+)"
                        )[0]
                        .dropna()
                        .astype(int)
                    )


                    if medicoes_t2_numeros.empty:

                        raise Exception(
                            "Nenhuma medição "
                            "numérica encontrada."
                        )


                    # ----------------------------------------------
                    # MAIOR MEDIÇÃO
                    # ----------------------------------------------

                    maior_medicao = (
                        medicoes_t2_numeros.max()
                    )


                    print(
                        f"📌 Maior medição: "
                        f"{maior_medicao}"
                    )


                    # ----------------------------------------------
                    # LOCALIZA LINK
                    # ----------------------------------------------

                    link_maior = wait.until(
                        EC.presence_of_element_located(
                            (
                                By.XPATH,
                                f"//a[normalize-space(text())="
                                f"'{maior_medicao}']"
                            )
                        )
                    )


                    # ----------------------------------------------
                    # ROLA ATÉ O LINK
                    # ----------------------------------------------

                    driver.execute_script(
                        """
                        arguments[0].scrollIntoView({
                            block: 'center'
                        });
                        """,
                        link_maior
                    )


                    time.sleep(0.5)


                    # ----------------------------------------------
                    # CLICA VIA JAVASCRIPT
                    # ----------------------------------------------

                    driver.execute_script(
                        "arguments[0].click();",
                        link_maior
                    )


                    # ----------------------------------------------
                    # AGUARDA ÁREA DA MEDIÇÃO
                    # ----------------------------------------------

                    wait.until(
                        EC.presence_of_element_located(
                            (
                                By.ID,
                                "medicaoExibe"
                            )
                        )
                    )


                    time.sleep(1)


                    # =================================================
                    # XPATH TABELA 4
                    # =================================================

                    xpath_t4 = (
                        '//*[@id="medicaoExibe"]'
                        '/div[3]/div[2]/table'
                    )


                    # ----------------------------------------------
                    # EXTRAI TABELA 4
                    # ----------------------------------------------

                    df_tab4_full = extrair_tabela(
                        xpath_t4
                    )


                    if (
                        df_tab4_full is None
                        or df_tab4_full.empty
                    ):

                        print(
                            "⚠️ Tabela 4 encontrada, "
                            "mas sem dados."
                        )

                    else:

                        # ------------------------------------------
                        # PEGA SOMENTE ÚLTIMA LINHA
                        # ------------------------------------------

                        df_tab4 = (
                            df_tab4_full
                            .tail(1)
                            .copy()
                        )


                        # ------------------------------------------
                        # ADICIONA SUFIXO T4
                        # ------------------------------------------

                        df_tab4.columns = [
                            f"{col} T4"
                            for col in df_tab4.columns
                        ]


                        print(
                            "✅ Tabela 4 extraída "
                            "com sucesso."
                        )


                except Exception as e:

                    print(
                        "⚠️ Erro ao extrair "
                        "tabela 4:"
                    )

                    print(
                        e
                    )


                # ==================================================
                # PREPARA TABELA 1
                # ==================================================

                df_t2["Medição"] = (
                    df_t2["Medição"]
                    .astype(str)
                    .str.strip()
                )


                # ==================================================
                # PREPARA TABELA 2
                # ==================================================

                if df_t3 is not None:

                    if "Medição T3" in df_t3.columns:

                        df_t3["Medição T3"] = (
                            df_t3["Medição T3"]
                            .astype(str)
                            .str.strip()
                        )


                        df_t3 = df_t3.rename(
                            columns={
                                "Medição T3":
                                    "Medição"
                            }
                        )


                    elif "Medição" in df_t3.columns:

                        df_t3["Medição"] = (
                            df_t3["Medição"]
                            .astype(str)
                            .str.strip()
                        )


                # ==================================================
                # MERGE TABELA 1 + TABELA 2
                # ==================================================

                if (
                    df_t2 is not None
                    and df_t3 is not None
                ):

                    df_merge = pd.merge(
                        df_t2,
                        df_t3,
                        on="Medição",
                        how="outer"
                    )


                elif df_t2 is not None:

                    df_merge = df_t2.copy()


                elif df_t3 is not None:

                    df_merge = df_t3.copy()


                else:

                    continue


                # ==================================================
                # ADICIONA CONTRATO
                # ==================================================

                df_merge.insert(
                    0,
                    "contrato",
                    contrato["contrato"]
                )


                # ==================================================
                # ADICIONA MUNICÍPIO
                # ==================================================

                df_merge.insert(
                    1,
                    "municipio",
                    contrato["municipio"]
                )


                # ==================================================
                # ADICIONA TABELA 4
                # ==================================================

                if (
                    df_tab4 is not None
                    and not df_tab4.empty
                ):

                    for col in df_tab4.columns:

                        df_merge[col] = (
                            df_tab4[col].iloc[0]
                        )


                # ==================================================
                # GUARDA RESULTADO
                # ==================================================

                dados_medicoes_merged.append(
                    df_merge
                )


                print(
                    f"✅ Contrato "
                    f"{contrato['contrato']} "
                    f"processado com sucesso."
                )


            except Exception as e:

                print(
                    f"❌ Erro geral no contrato "
                    f"{contrato['contrato']}:"
                )

                print(
                    e
                )


        # ========================================================
        # SALVA CSV DA TABELA PRINCIPAL
        # ========================================================

        if dados_contratos:

            df_contratos = pd.DataFrame(
                dados_contratos
            )


            df_contratos.to_csv(
                os.path.join(
                    path,
                    "info_test.csv"
                ),
                sep=";",
                index=False,
                encoding="utf-8-sig"
            )


            print(
                "✅ info_test.csv salvo!"
            )


        else:

            print(
                "⚠️ Nenhum dado da tabela "
                "principal para salvar."
            )


        # ========================================================
        # SALVA CSV FINAL
        # ========================================================

        if dados_medicoes_merged:

            df_final = pd.concat(
                dados_medicoes_merged,
                ignore_index=True
            )


            df_final.to_csv(
                os.path.join(
                    path,
                    "test.csv"
                ),
                sep=";",
                index=False,
                encoding="utf-8-sig"
            )


            print(
                "✅ test.csv salvo!"
            )


            print(
                f"   ↳ Total de linhas: "
                f"{len(df_final)}"
            )


        else:

            print(
                "⚠️ Nenhum dado final "
                "consolidado."
            )


    except Exception as e:

        print(
            "❌ Erro no processo "
            "test:",
            e
        )

        raise


    finally:

        driver.quit()

