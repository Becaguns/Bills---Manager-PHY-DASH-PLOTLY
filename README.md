Sistema de gerenciamento de contas, com graficos integrados interativos

Roadmap para execucao da tarefa


Definicoes principais
  Pasta que  a aplicacao ficara instalada = py
    Banco de dados = PostgreSQL
      Database name = sentinel
        Database nao possui nenhuma tabela ou coluna todas terao que ser criadas
          Usuario = Andrino
            Senha = Rebecca@2023
              Ip do Servidor = 192.168.100.100
                Sistema operacional = Fedora server
                  Servidor esta instalado em um Raspberry pi 4 


1 - Criar tela de login, baseado no arquivo dashboard.html
     * Nome da tela de Login  Wallet Sentinel
      *  Rodape da tela de login com texto = Sua liberdade financeira depende da sua disciplina.
        *  Criar CSS para os botoes de login interativo, com  icones que remetam sistemas modernos
          *  Os botoes podem com animacoes bounce, and shake 
            * Este css criado sera o tema global de toda a aplicacao 

2 - Efetuar testes de conexao com banco

3 - Integrar o dashboard.html para ser acessado apos a tela de login
      Criar CSS para o dashboard.html para que seja igual o tema da tela de login.

4 - Agora que ja temos um dashboard e a sidebar vamos implemetar alguns graficos, na tela do lado da sidebar vamos fazer o fazer a seguinte divisao 
    *   Um retangulo com as seguintes dimensoes \
  /* Estilo para o retângulo */
.rectangle-4 {
    width: 360px;
    height: 276px;
    padding: 8px;
    background: linear-gradient(144deg, rgb(23, 23, 23) 0%, rgb(17, 17, 17) 99%);
    border-radius: 16px;
}

/* Estilo para o título */
.proventos-x-despesas {
    width: 230px;
    height: 31px;
    color: #FFFFFF;
    font-family: "Nunito Sans";
    font-weight: 600;
    font-size: 22px;
    letter-spacing: -0.2px;
    text-align: left;
}

Dentro desse retangulo iremos inserir o seguinte grafico  


Funcao para cor gradiente 1 linha Proventos

let width, height, gradient;
function getGradient(ctx, chartArea) {
  const chartWidth = chartArea.right - chartArea.left;
  const chartHeight = chartArea.bottom - chartArea.top;
  if (!gradient || width !== chartWidth || height !== chartHeight) {
    // Create the gradient because this is either the first render
    // or the size of the chart has changed
    width = chartWidth;
    height = chartHeight;
    gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
    gradient.addColorStop(0, Utils.CHART_COLORS.blue);
    gradient.addColorStop(0.5, Utils.CHART_COLORS.yellow);
    gradient.addColorStop(1, Utils.CHART_COLORS.red);
  }

  return gradient;
}

// Função para inverter o gradiente 2 linha Despesa 
function getReversedGradient(ctx, chartArea) {
  const gradient = ctx.createLinearGradient(chartArea.left, 0, chartArea.right, 0);
  gradient.addColorStop(0, 'blue'); // Cor final da original vira a inicial
  gradient.addColorStop(1, 'red'); // Cor inicial da original vira a final
  return gradient;
}

o Config do graffico  editar como for mais eficaz para a nossa aplicacao

const config = {
  type: 'line',
  data: data,
  options: {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
    }
  },
};

Setup do grafico  Mudar para tratar o mes e o valor de R$: 3000 ate  R$: 25000

const DATA_COUNT = 7;
const NUMBER_CFG = {count: DATA_COUNT, min: -100, max: 100};
const labels = Utils.months({count: 7});

const data = {
  labels: labels,
  datasets: [
    {
      label: 'Dataset 1',
      data: Utils.numbers(NUMBER_CFG),
      borderColor: function(context) {
        const chart = context.chart;
        const {ctx, chartArea} = chart;

        if (!chartArea) {
          return;
        }
        return getGradient(ctx, chartArea);
      },
    },
    {
      label: 'Dataset 2', // Segunda linha com cores invertidas
      data: Utils.numbers(NUMBER_CFG),
      borderColor: function(context) {
        const chart = context.chart;
        const {ctx, chartArea} = chart;

        if (!chartArea) {
          return;
        }
        return getReversedGradient(ctx, chartArea);
      },
    },
  ]
};

E as acoes do grafico 

const actions = [
  {
    name: 'Randomize',
    handler(chart) {
      chart.data.datasets.forEach(dataset => {
        dataset.data = Utils.numbers({count: chart.data.labels.length, min: -100, max: 100});
      });
      chart.update();
    }
  },
  {
    name: 'Add Data',
    handler(chart) {
      const data = chart.data;
      if (data.datasets.length > 0) {
        data.labels = Utils.months({count: data.labels.length + 1});

        for (let index = 0; index < data.datasets.length; ++index) {
          data.datasets[index].data.push(Utils.rand(-100, 100));
        }

        chart.update();
      }
    }
  },
  {
    name: 'Remove Data',
    handler(chart) {
      chart.data.labels.splice(-1, 1); // remove the label first

      chart.data.datasets.forEach(dataset => {
        dataset.data.pop();
      });

      chart.update();
    }
  }
];


5- Incluir funcao ao dashboard criando um novo arquivo chamado despesas.html
  * funcao do arquivo, quando clicar no botao presente hoje no dashboard, abrir tela de inclusao de despeas na tela ao lado da sidebar
      * Comportamento ao clicar no botao de incluir despesas a tela ao lado faz um flip como se tivesse girando a pagina e mostrando a pagina de traz.
          * Nessa nova pagina teremos os seguinte elementos todos na mesma linha 
              1 selecionador data no formato ddmmaaaa, com a descricao encima
                Este botao precisa ter um mini calendario para selecao da data
              2  Caixa de texto para inclusao da descricao da despesa
              3  caixa de texto para inclusao do valor da despesa com mascara R$ = real brasileiro BRL   acima desse campo um checkbox para tratar se a divida e recorrente
              4  Uma caixa de  texto para inclusao do tipo de despesa obs esse pode ser um select box para selecionar os tipos de despesa mais comuns do ser humando uns 7 tipos basicos esta otimo
              5 dois date pickers igual ao primeiro mas esses serao condicionados ao checkbox de recorencia se for marcado eles serao ativados para inserir uma data de incio e outra de fim, se nao for marcado sera                   considerado com conta de pagamento unico
              6 Abaixo dessa linha uma planilha ira mostrar as despesas incluidas recentemente  acima dessa planila tera um botao editar cada linha da planilha tera um checkbox para que se ele tiver selecionado 
                essa linha se torna editavel mas somente ela e um botao o botao de editar da um flip  e vira botao de salvar.
          
