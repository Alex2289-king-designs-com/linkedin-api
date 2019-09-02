import requests
import pickle
import logging

import linkedin_api.settings as settings

logger = logging.getLogger(__name__)


class ChallengeException(Exception):
    pass


class UnauthorizedException(Exception):
    pass


class Client(object):
    """
    Class to act as a client for the Linkedin API.
    """

    # Settings for general Linkedin API calls
    API_BASE_URL = "https://www.linkedin.com/sales-api"
    REQUEST_HEADERS = {
        "user-agent": " ".join(
            [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5)",
                "AppleWebKit/537.36 (KHTML, like Gecko)",
                "Chrome/66.0.3359.181 Safari/537.36",
            ]
        ),
        # "accept": "application/vnd.linkedin.normalized+json+2.1",
        "accept-language": "en-AU,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
        "x-li-lang": "en_US",
        "x-restli-protocol-version": "2.0.0",
        # "x-li-track": '{"clientVersion":"1.2.6216","osName":"web","timezoneOffset":10,"deviceFormFactor":"DESKTOP","mpName":"voyager-web"}',
    }

    # Settings for authenticating with Linkedin
    AUTH_BASE_URL = "https://www.linkedin.com"
    AUTH_REQUEST_HEADERS = {
        "X-Li-User-Agent": "LIAuthLibrary:3.2.4 \
                            com.linkedin.LinkedIn:8.8.1 \
                            iPhone:8.3",
        "User-Agent": "LinkedIn/8.8.1 CFNetwork/711.3.18 Darwin/14.0.0",
        "X-User-Language": "en",
        "X-User-Locale": "en_US",
        "Accept-Language": "en-us",
    }

    def __init__(self, debug=False, refresh_cookies=False):
        self.session = requests.session()
        self.session.headers = Client.REQUEST_HEADERS

        self.logger = logger
        self._use_cookie_cache = not refresh_cookies
        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)

    def _request_session_cookies(self):
        """
        Return a new set of session cookies as given by Linkedin.
        """
        if self._use_cookie_cache:
            self.logger.debug("Attempting to use cached cookies")
            try:
                with open(settings.COOKIE_FILE_PATH, "rb") as f:
                    cookies = pickle.load(f)
                    if cookies:
                        return cookies
            except FileNotFoundError:
                self.logger.debug(
                    "Cookie file not found. Requesting new cookies.")

        res = requests.get(
            f"{Client.AUTH_BASE_URL}/checkpoint/lg/login-submit",
            headers=Client.AUTH_REQUEST_HEADERS,
        )

        return res.cookies

    def _set_session_cookies(self, cookiejar):
        """
        Set cookies of the current session and save them to a file.
        """
        self.session.cookies = cookiejar
        self.session.headers["csrf-token"] = self.session.cookies["JSESSIONID"].strip(
            '"'
        )
        with open(settings.COOKIE_FILE_PATH, "wb") as f:
            pickle.dump(cookiejar, f)

    def authenticate(self, username, password):
        """
        Authenticate with Linkedin.

        Return a session object that is authenticated.
        """
        self._set_session_cookies(self._request_session_cookies())

        payload_of_mine = {
            "csrfToken": "ajax:3262632008743939867",
            "session_key": username,
            "ac": 0,
            "sIdString": "24566084-5d4a-4b4e-b42d-60e5ad5fee77",
            "controlId": "d_checkpoint_lg_consumerLogin_navigator-login_submit_button",
            "parentPageKey": "d_checkpoint_lg_consumerLogin_navigator",
            "pageInstance": " urn:li:page:d_checkpoint_lg_consumerLogin_navigator;BEzUE4yBS1KL2G6cgNyAEw==",
            "trk": "navigator",
            "session_redirect": "/sales",
            "loginCsrfParam": "5494a38c-cb32-4a9d-8e43-4f9dcf70adbc",
            "fp_data": {"X-kcnN2cez-f": "AwIHlXRpAQAAImHbUFfTzoZj1Eyqi8fC6QjI9Fmx9REX3bPOsas9PjU3F-c3AX8AAAGLr4YowLkAAAAAAAAAAA==", "X-kcnN2cez-b": "yaxiao", "X-kcnN2cez-c": "AwIHlXRpAQAAImHbUFfTzoZj1Eyqi8fC6QjI9Fmx9REX3bPOsas9PjU3F-c3AX8AAAGLr4YowLkAAAAAAAAAAA==", "X-kcnN2cez-d": "o_0", "X-kcnN2cez-z": "p", "X-kcnN2cez-a": "OJ-7A5_hRuGSh=SDqGvZaH74bVOLBMA6tG8fvvIp2kOKJph1FG8eXa26Vzd=uEQ8mGjufL41JYOVufZ73SP6myyKeweR-xuzcFgni3YZGUsNOfjFpx5i6RuY-6xfnwixZedkohzk0VvhHC1AlQucisN3iDfVNR4r_KlkExK_0iDTLElOVRo48V26G9U8MYu_n8a7GIrCwrYO=FexoDZ2_p15rz6vonQH_hgxMIeM4_bgGK86Isz3YYV2z3LOTgvS5ttNljD_=CXtgThahDpdxFR_0MCHhsriJ-EgSYA1o8VaFU84xiRxeLFtZ8QNg44Y7MBf8kUC-G6tpCMPLtpcSMhnzhLU1D6nuEv_dGo10eT9HpgnE0peRsCaoJIgNV1FkJtsvor5USsM-BpJER0tZg9ktJw0Ns-VtCFteo3Yc1C7thRAa4Sf4llgqbV8UmtQTOCjpnk8GZmYrTBDv97hiLdEd8aKOBoxN1_IlkPV-uDjQ0NxE0384KSOCIaSUE33mE7gtQiLgI7Z3yvwzRS8Lb7QI7sbBvzxkyurp8d=LunoEBPsY5FlLzT6Jmz3iGO9Qw=Px7r5iH_i35XwoEbR0VVcZxXtQoPXtmRESZ3tBTMrSCjXOZ0Qrwcod6_BY8U58vhMNcvFhc5rvNpiAM_KZN=5h44vhp054YA=eoxv2jVmoNE9dTxq4LNgiZVrhVOHZ0oyxgUXodjbUH1gx3yo5aG_5vq2V2TkNG94nql-I1n5Xucft=UuPI2oqyxDIU5yxyKleP5ZzNMZGdqUNlPA7HkwFX7AVDF_DUyzy_z2ZS53DRxO7uO-d9uQ9goM3Z-rcQcs3iBzbtV45pBRZqdaqL5Q3oaO2QcY81=m63p7egTlLqe=l7kyvzyK_t9Is6Hz=oMawx6mxIGx09nOnmvuh16ZoDqvqbZshuDlS4AQIGekjY0Uyqkaw40G7=Ti83iyB9-rhhoywkkwK_YN3fnT=0Zs_=ZSEPCs4Y9p0ax=Lpq3FnsaoXgwA8HBj0eatONjR2Vpm0UCOXtpQjT9KzRw4__BZ397rBg7ztz=-KVrDwxQ1-VgLf3D65r8rTgT1EPAGIIsv1jHKszEpf1TEZ731PHP-Hw_TgU5s6SVTUd0nygB4jtw_xeduHVgkMFxVq0H-wdODX6_KI3XGatDISCxHiQZrbrBnJTfFEuXvf29ZogyvnhaG7sptcP003L=qSenIFJ_8IENX2ftHHgPpK77j_PVZdNbOUAYPNjfc8RNfSVyF_eP2ePIKzElXyuKjr_lxbB8lHAXmfVao5UqEIwSAiZipyijmqu-XvT=yeg0V6rG3xJe9sO75FUBOew4VBMQGq2u1ot_96FGLLDp-gGJ70apnftRB29pshwEnzSIxc6EqhUH9mhreNi1QaUqk=NkYUM7mEubDsmZ67y9xjTECAqimOLfPBPq6Re=GTB_PDR=8vH1Lqv1fBKEGJ7PstPiwS79hmTZRrht31a=mZ69aH39=3oCKtGfhc2RAtIBKrHJePzuTh6xroeReo3i8fwJkiVBLGIy9lUYvz4ymcbR1HiVDC5TT__11XkNZACeiJfupQaLKXhEZUHu1andvhBcYdAxSAersf3ojVEhZORxEnwAEumevI2EAoZNhvvPJc8koCeke-BLUGKOAxjV2mK0SMbhiXnTtKsmsBRdvPOUBYon82pRfwn6xB-pozldxzvayTydHRTMN7tfXhOvIBi=PGOqS_=vMPocA_lx2FBLt0kqRfbF1QZGjCi1JQuhYlpYdd5k_4OjLLKhVTT5yLIxkTqs9oJAB7kdaOTf_vkqNXHzJr95tDKlURo7TV7H8SjhA8CuLAVux7LFFIuydhZhC9dI3=a-Iq4GLOw=RI4yHyZSmEG8Ut6a3vv4L061AOOJSG3GvkK-qBRXRz-gARdILNUFnRtk24e1BOqG5ylfNlIGIG0p9gSHJ0iDyFl_=zzRSL=mtUJXKIbTxT1gL1JMD0_2z2FEN57ijoPhXBaM4sSS8DNmxa3fm-VXxeGe2ZSFlntDjymBqvSinIXdBvfJEBUDzBcUwBkfcR19l5CnnibmSQXwVq_U4A9aLBx_5JQlPIQBIk6wJXYl9uXI1uvhofhJekE9Lp1PULTbA4tTSTM3wKyD=oCgPojnNQAHuXPxU1b-BiqZJZ33_NSX=bhfeNrA=kfDU48X86e7xs-VfrxdUqMoGCuBOJu1v0VMqu=V1Aw9Nzf0ZhiX=cFrCHY-UJxpUHvgm63yoIFTTQzGsy4x7mFennGNF_Jf-iGsPoCwx4QmJCaQ2qtyrYbvqJ48VcTB8tpPRprr9U-qbmuG-bJIaH34l33x3AReihahxQ9VLiT60uiFpuSS7Pmu_clDq4Z1j02ZpyOxrMhyBlhlc-0z=zSF9pYDnZ5NOI-CBSQZwnQdgGko0sO59c02RERJ0IgI6vXyy7qA02_sRm_TPruwpm-3vXih3nwvDt1COTpCJTwX4K4wwpGC6UBPGMmdyhtnwJHpTcjB37ea0HnyfdaqfItX5=2jDKLPL9UR5cOFUdNwQfOfeEfwXis728hLo1C7ZS7KQzuZYZ1jyZ2VHTBGxHbagbmN71-yocelouddwajucoxrgYU-jXb9s01wCGiuzouydmOIJ0XxKvA=9JCVrQKKkrhD-N-ZciACyR=23yISBCyB5A9KylTs9xG2LaJYCe5rH3Stdr1ya=2VE881lDvVpa6lwMa-wL7mQNv1I1j1_IglN65pq9SG_-x43uaGXqBxe6NfsIkeDjRN8f3xX3cbOQ48VIz-7AKwyXzCDu8tVPc_Yw_nAwNOO2YT1L6Alt3cKhMYJ=8jS1vxJ3BOPVnb8FSVQ2Okmf4hkEi63Tn0haziZdzHde4jbXmwQuERHA-guJ3OYel84kDgVpK-2D4Q5oeNGq9pz8gqaM_iL0ebZQEaqsoBy4-zfUgTwUtgtFVIfNUsOvejh3_vJqpy2zNK1Vj6153pawthXLIm8oPRDZPCRrPklIP-pqPoonREBKAZf=EpJJ0i4qU__=sgTNbNYmmrlKxqOz1LYlSuoTav7TGSOUZKslz2kol44eslai3k1Ig0LURi5pR02vr8QAKo-ZlZbiy72xSqJRO1--4h4jB4ZtLL99uP1qB4toRP=eAS7JHMxt9nTbc_6hTE-v67k31yV5wE6Dm227zZM_u7XScp=iYuXVqwvZ_F5KnkHUfqiqCgFH_x6uKVcKl2YxlxtwNXkbvKf4fa-dGa3s2qGKyHAfPOnERQQi629nKTv1wmi0vA0d0q_VvnAct9hUSlLMMN8gmhiikL0DAiy0f14Ln9aXmb2jXorz6vqurqzOs5on1eIwQ-bnSEvI2M62TxNMCN5JXfNH0LvL-0AKj283Qw1qCtdGuOEbEoMg=POCTi5mGxELdlb=XSh8Cj3Sf7AY7ua5a8cX8IjkGy-txSlt=VCFzF7_XVHd-6gyXDK2-6mHIlINB-U=oeCwCZ3Xcg0BXO6VJ8FkVHgQVhTXIOwsY51DhfpdfSDoRhSHdHS70FeujLfUwB6D_ZAUi52BnNAtNNbfG0JCty5vE9r1xEnq6dE6iX-gertToOiqdK-=KHuFU9Nu61RrIDDvBTu-9F_1wEbXZ6F2NXtD7=xOKvBpmw9aHoyTKuMblZ_NCdg0OnDG-fKLjXL4MqA2_lh9gzhZ79bB-MdmmHZYR-GsyYuCxffsJ4gLeHJ1fplmxLgXgcepYYmHsh_=PotdTDqYhFlbdCGUmBL35dNBUSZJ-BTKG=GHLwd1tFnJSLGT=j8CN_GofhwdSHOZad1QvahesPOXDjb_glqxy0-M2zKEpjhU42ZFHTdEZz6GxjLb-3wMU6jGIO0=kIq4rl-0EtIzut7=b_KL==x5yTDiPCuSlmqkhi_zsB4el9BP4DeF6Xpmf17GGfupXlIT4-LG7k2taVzCOVZyDYRninH_-YZHvhAUrDjlJaRpNShVZzML0zNyFO-m9w-TkebY_Tm8tmK7pf6aswiLVcAple47yBI8MfjbPMskaZCfEBKMz12TCKFqIywryTTYOpY2IDlrlL7uKTFrjdpluRySiXXyaMPwG9b4QjCbm-oyuqtGKHRRMUnu=ZJBoQTipqDBjXFJ=JBbe-5sHBnoaEIw48B97xHhFNjDU7LsIv1rkOYQ4f6KtwOTgXdipTKsrS7PG-9wyBAva9wK2QJQ7raj7uHR7_q6VtiBeCXw8vCn4Y1DF2uAn5IxzOlZjlfNe_nJ8ZIPsDed5NPJsL-oY3aeCQ4idu2n5HKvjH8=32CeYRiLqmbgzkANHB_he5LSXVuhEL8wPd62XqBUHlciZFgO6xux9GlFQ-9kO12399ttG8y8SCru-B5iy8GgqAPuZx85Ocp7LciQ13RwzB53PbSoizOV7iqnq_k_oS678yK1kXts8meXzam6bysqU6=6uSq-bgxOzHYmON=0GAYfa5VABVolaJzYkpBwMrKbqhG8kJMlI3M=0QemeYga0A7a8oq-OVvmuiDPCFCmmsgxkwB71Hk58C71Jmo5q=FJ8ucIogbecS2UwxgrieZmrCb8xBpCxlVvAokH4VZPaHd1QKmDkayTdCGICU1ZkiTDseKMcvgHGf3HaDYajFNG97nMwO9MFrMLKHxpLmXVi8QMf2ABSerOJMP_xKVOocjz99m5r4Eo7kInhAuduZ=_lXAuCiB7wBLMmRs1C3IvoQSjJnRuUxOgof3zMeLtxVR52rtEeOokG5BTTRwX5hwitPqpDr2pGjpwXLpsc1Tm=YNXkqL1yCSA45ksqbc7-qgD-R2gAQsvXnZhKNRYvRRoe31nR8i9haXaNIc4-0j4dja0p2qAQsLGr-3z4M1Gwvb-MgJx_i0Fu8NOSDjo5Ce1xgelC1sN0OpLocVsGFOON50KCsPF17OdsUbK_sFbtGNyMhgmBr-lORbZCRhszgbm9cuv4eztvNkSVRMuHNRzyIKb4grdbu-IjJyv91r7a1B0aRFK-lHhmjt2TAXI13yEYiHN3BbL_3tk6RGZS2JCFi03eo=MPCI4Izx83Es9o6UeAgYPFTCYB8=tfDOzRHclGufqO4StrVvub33N-prIiK48GxJEuejlyX-IQGwOUaOa5oLpHagZnXynt0RZUhUVqo_r_H2_Uq4eqdBmj4ARUymH9qFXflHNKcitS6KeS9OErZxcQ7F4Z1VgAsVQ-6uYL0r6_SClyr4NxYwsE2MlRhidbEMjrQsZ=LNjCiGzyjsbxdYvGIZI8Axwclh1Hm0IK2tc4SpuFnUGHa=7vjmFcsSi4qOlCoHLiL2s91D4fG_TGIqdQeA1_NK1Iue=rPfGF9iN-25HFpZ1Sc=M_QuEju=58tNoSJEOjKtXT23NBK1fhR5xBd1-NU_H1bv2Ph2O8XdB5L5tb5EOqDyJtkH-yKmQoSnx58vgGnRuYHqhtxOqLM5yqti5=1-yVD53fgKcqbVyrHYDNns8Dbdx2I9vCKxViyoO3jQ0lxHVu_gH1"},
            "_d": "d",
            "_f": "navigator",
            "session_password": password,
            "JSESSIONID": self.session.cookies["JSESSIONID"]
        }

        res = requests.post(
            f"{Client.AUTH_BASE_URL}/uas/authenticate",
            data=payload_of_mine,
            cookies=self.session.cookies,
            headers=Client.AUTH_REQUEST_HEADERS,
        )

        import ipdb
        ipdb.set_trace()

        data = res.json()

        if data and data["login_result"] != "PASS":
            raise ChallengeException(data["login_result"])

        if res.status_code == 401:
            raise UnauthorizedException()

        if res.status_code != 200:
            raise Exception()

        self._set_session_cookies(res.cookies)
