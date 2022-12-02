# Projeto do B2 - CCI36 - Radiosidade

**Autores:** 

- Thiago Lopes de Araujo
- Gabriel Henrique Gobi

----------
## Introdução

<div style="text-align: justify">
No ramo da computação gráfica, a radiosidade compreende um problema clássico de determinação do padrão de iluminação de uma cena. 

Tal conceito advém do tratamento físico de radiação emitida $(B)$ por um corpo frente ao sistema ao qual está incluso, sendo, nesse viés, a iluminação de um objeto determinada não apenas por sua emissão natural $(E)$ - não nula no caso de um corpo luminoso - mas sim pela emissão natural adicionada ao somatório de interfências com a energia refletida multiplicada por um fator intrínseco $(ρ_r, ρ_g, ρ_b)$ de cada corpo, determinante de sua cor natural.

Dessa forma, a determinação da radiosidade pode ser traduzida como a resolução de um sistema linear composto pela adição da terna de equações abaixo para cada participante da cena:
<div>


$$
B_r = E_r + \rho_{r} I_r
$$
$$
B_g = E_r + \rho_{g} I_g
$$
$$
B_b = E_r + \rho_{b} I_b
$$

Sendo $(r,g,b)$ a divisão unívoca de uma cor em componentes vermelho, verde e azul.

Cabe ressaltar que os termos $(I_r, I_g, I_b)$ da iteração entre objetos podem ser determinados por meio do cálculo do fator de forma - o quanto de energia é transmitida na interação - conforme abaixo:

$$
F_{i-j} = \int_{A_i} \int_{A_j} \frac{\cos \theta_i \cos \theta_j}{\pi r^2} \ dA_i \ dA_j
$$

Sendo os parâmetros acima expostos a seguir:

<img src=".//images/shape_factor.png"  style="display: block; margin: 0 auto; width:400px;"/>

Por meio do fator de forma, o sistema linear é modelado conforme conjunto de equações:

$$
B_i = E_i + \rho_i \sum_j F_{i-j} B_j
$$

Dessa forma, o sistema pode ser traduzido para a seguinte multiplicação de matrizes (forma utilizada no transcorrer do projeto):

$$
A_{n,n} \ B_n = E_n 
$$

$$
  A_{n,n} = \left[ {\begin{array}{cccc}
    1 - \rho_1 F_{1-1} & - \rho_1 F_{1-2} & \cdots & - \rho_1 F_{1-n}\\
    - \rho_2 F_{2-1} & 1 - \rho_2 F_{2-2} & \cdots & - \rho_2 F_{2-n}\\
    \vdots & \vdots & \ddots & \vdots\\
    - \rho_n F_{n-1} & - \rho_n F_{n-2} & \cdots & 1 - \rho_n F_{n-n}\\
  \end{array} } \right] 
$$

## Parte 1 - montando a cena no Blender

Utilizando-se a versão do Blender 3.3.1, construiu-se a cena a seguir:

<img src=".//images/developed_scene.jpg"  style="display: block; margin: 0 auto; width:400px;"/>

Cabe ressaltar que o *wireframe* construído a fim de calcular a radiosidade apresenta uma resolução de 948 faces triangulares, disponibilizadas conforme abaixo:

<img src=".//images/wireframe.png"  style="display: block; margin: 0 auto; width:400px;"/>

## Parte 2 - Extraindo as informações dos arquivos

Exportando-se o arquivo no formato COLLADA (.dae), pôde-se inspecionar a geometria e as cores de acordo com a modelagem feita no Blender. O arquivo .dae, no fundo, se trata de um arquivo XML. Utilizando a biblioteca XMLTree de Python, pôde-se recuperar os vértices de cada face e suas cores. Com essas informações, calculou-se também as normais, por um produto vetorial normalizado de duas arestas da face triangular, a área e o centroide. Como as cores eram definidas para os vértices, calculou-se a cor de cada face como a média das cores de seus três vértices.
  
Após a leitura do arquivo, populou-se estruturas de dados definidas em código ```Vertex```, ```Triangle``` e ```Object3D```, de forma a se conseguir facilmente recuperar qualquer informação referente à cena durante o cálculo da radiosidade.

## Parte 3 - Computando a Radiosidade e substituindo as cores nos arquivos

Da extração de informações, em associação com o arcabouço teórico exposto anteriormente, determina-se inicialmente a matriz:

$$
A_{n,n} = \left[ {\begin{array}{cccc}
    1 - \rho_1 F_{1-1} & - \rho_1 F_{1-2} & \cdots & - \rho_1 F_{1-n}\\
    - \rho_2 F_{2-1} & 1 - \rho_2 F_{2-2} & \cdots & - \rho_2 F_{2-n}\\
    \vdots & \vdots & \ddots & \vdots\\
    - \rho_n F_{n-1} & - \rho_n F_{n-2} & \cdots & 1 - \rho_n F_{n-n}\\
  \end{array} } \right]
$$ 

Cabe ressaltar a simplificação no cálculo do fator de forma de cada componente acima na tentativa de redução da demanda computacional necessária - e consequente diminuição do tempo dispendido:

```python
def _get_shape_factor(self, i, j):
        """
        Calculate the shape factor between two faces.
        Fij ~ cos(phi_i) cos(phi_j) * Aj / (pi * r^2)
        """
        if i == j:
            return 0.0
        else:
            if self._is_object_between(i, j):
                return 0.0
            else: 
                theta_j = self._get_angle_between_faces(i, j)
                theta_i = self._get_angle_between_faces(j, i)
                if theta_j <= np.pi/2:
                    return 0.0
                else:
                    r_2 = np.sum(np.power(self._t[j].centroid - self._t[i].centroid, 2))
                    return np.cos(theta_i) * np.cos(theta_j) * self._t[j].area / (np.pi * r_2)
```

A solução foi obtida, portanto, do método ```np.linalg.solve``` da biblioteca ```numpy```, que resolve via LAPACK o sistema por fatoração LU, de forma que o vetor de emissões resultantes $(B)$ fosse armazenado para modificação do arquivo de cena construído.

```python
 def solve(self):
        """
        Solve the radiosity linear system.
        A @ B = E
        """
        for c in range(self._NUM_COLORS):
            self.B[:, c] = np.linalg.solve(self.A[:, :, c], self.E[:, c])
        file_B = open("./utils/numpy_files/B.npy", 'wb') 
        np.save(file_B, self.B)
```

Ao término da sobrescrita do arquivo original, obteve-se o seguinte padrão de iluminação da cena:

<img src=".//images/scene_gamma1.jpeg"  style="display: block; margin: 0 auto; width:400px;"/>

Dessa forma, optou-se por efetuar empiricamente a correção gamma do padrão obtido, de forma a obter o seguinte resultado para $\gamma = \frac{1}{3}$:

<img src=".//images/scene_gamma_1_3.jpeg"  style="display: block; margin: 0 auto; width:400px;"/>

Por fim, evidencia-se a corretude da implementação dado as condições de contorno impostas. Veja, por exemplo, o objeto vermelho (simulando-se um livro em estante) provocando iluminação parcialmente vermelha observável na proximidade da parede.

Observe também como a claridade decai com o afastamento das faces em relação à lâmpada, como a base da mesa permaneceu escura (efeito de sombra do tampo) e como as paredes, originalmente claras, ficaram amarronzadas pelo reflexo da cor do tampo da mesa, objeto mais bem iluminado pela lâmpada.
  
Ainda assim, o resultado não é tão homogêneo. Isso ocorre principalmente devido ao grau de divisão escolhido para a construção do _wireframe_ dos objetos e à aproximação da integral do cálculo do fator de forma. Com essa configuração, já se demorou em torno de 4 horas para o cálculo de todos elementos da matriz $A$. Caso se desejasse maior precisão, seria necessário não só aumentar a discretização do _wireframe_, mas também aprimorar-se o código (com _multithread_, por exemplo) para tornar viável o cálculo de radiosidade pelo método proposto. 

Contudo, uma vantagem do método utilizado é que, uma vez calculada a matriz $A$, que contém toda a geometria da cena, pode-se facilmente alterar os objetos luminosos e suas cores, variando-se somente o lado direito - vetor $E$ - e resolver o sistema - o que pode ser feito de forma computacionalmente eficiente e com baixo custo em termos de tempo demandado. Tal fato pode ser corroborado a se variar a fonte luminosa tendo como enfoque a seleção de um dos objetos na estante ao invés da lâmpada, sendo o resultado da variação exposto abaixo para cada diferente fonte luminosa selecionada:

Seleção do objeto naturalmente vermelho:

<img src=".//images/red_lum.jpg"  style="display: block; margin: 0 auto; width:400px;"/>

Seleção do objeto naturalmente azul:

<img src=".//images/blue_lum.jpg"  style="display: block; margin: 0 auto; width:400px;"/>

Seleção do objeto naturalmente verde:

<img src=".//images/green_lum.jpg"  style="display: block; margin: 0 auto; width:400px;"/>

Por fim, evidencia-se que, uma vez selecionada a fonte luminosa em quaisquer dos três modelos acima, acarreta-se um padrão de iluminação condizente com o esperado teoricamente dado a fragmentação do _wireframe_ utilizada. Além disso, cabe observar que não há reflexão dos dois objetos da estante não selecionados em relação ao objeto luminoso, sendo tal fato possível de se justificar dada a divisão em espaços disjuntos do espectro de cores em $(r,g,b)$ e, consequentemente, a emissão em uma componente não apresenta influência nas demais.