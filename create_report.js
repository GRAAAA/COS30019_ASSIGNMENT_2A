const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
  WidthType, ShadingType, VerticalAlign, PageNumber, PageBreak, TableOfContents,
  UnderlineType, ImageRun
} = require('docx');
const fs = require('fs');
const path = require('path');

// A4, 2.5 cm margins
const PW = 11906, PH = 16838, M = 1418;
const CW = PW - M * 2; // 9070 DXA content width

// ── Borders ─────────────────────────────────────────────────────────────────
const bThin  = { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' };
const bNone  = { style: BorderStyle.NONE,   size: 0, color: 'FFFFFF' };
const bBlue  = { style: BorderStyle.SINGLE, size: 8, color: '2E4057' };
const bGrey  = { style: BorderStyle.SINGLE, size: 2, color: '999999' };
const allThin = { top: bThin, bottom: bThin, left: bThin, right: bThin };

// ── Text helpers ─────────────────────────────────────────────────────────────
function t(text, opts = {}) {
  return new TextRun({ text, font: 'Arial', size: 22, ...opts });
}
function tb(text) { return t(text, { bold: true }); }
function ti(text) { return t(text, { italics: true }); }
function tc(text) { return new TextRun({ text, font: 'Courier New', size: 20 }); }

// ── Paragraph helpers ────────────────────────────────────────────────────────
function para(text, opts = {}) {
  const { bold = false, italics = false, after = 160, before = 0, indent = 0,
          align = AlignmentType.LEFT, size = 22, color } = opts;
  return new Paragraph({
    alignment: align,
    spacing: { before, after },
    indent: indent ? { left: indent } : undefined,
    children: [new TextRun({ text, bold, italics, font: 'Arial', size, color })],
  });
}
function mp(runs, opts = {}) {
  const { after = 160, before = 0, indent = 0, align = AlignmentType.LEFT } = opts;
  return new Paragraph({
    alignment: align, spacing: { before, after },
    indent: indent ? { left: indent } : undefined,
    children: runs,
  });
}
function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1, spacing: { before: 480, after: 200 },
    children: [new TextRun({ text, font: 'Arial', bold: true })],
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2, spacing: { before: 320, after: 160 },
    children: [new TextRun({ text, font: 'Arial', bold: true })],
  });
}
function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3, spacing: { before: 240, after: 120 },
    children: [new TextRun({ text, font: 'Arial', bold: true })],
  });
}
function bl() { return new Paragraph({ spacing: { after: 100 }, children: [t('')] }); }
function pb() { return new Paragraph({ children: [new PageBreak()] }); }
function bul(text, opts = {}) {
  return new Paragraph({
    numbering: { reference: 'bullets', level: 0 },
    spacing: { after: 100 },
    children: [new TextRun({ text, font: 'Arial', size: 22, ...opts })],
  });
}
function bul2(text) {
  return new Paragraph({
    numbering: { reference: 'bullets', level: 1 },
    spacing: { after: 80 },
    children: [t(text)],
  });
}
function code(text) {
  return new Paragraph({
    indent: { left: 720 }, spacing: { before: 60, after: 60 },
    children: [tc(text)],
  });
}

// ── Table cell helpers ────────────────────────────────────────────────────────
function tcell(paras, opts = {}) {
  const { w = 1000, bg = 'FFFFFF', valign = VerticalAlign.TOP, span = 1, shading = {} } = opts;
  return new TableCell({
    columnSpan: span,
    width: { size: w, type: WidthType.DXA },
    borders: allThin,
    shading: { type: ShadingType.CLEAR, fill: bg, ...shading },
    verticalAlign: valign,
    margins: { top: 80, bottom: 80, left: 100, right: 100 },
    children: Array.isArray(paras)
      ? paras
      : [new Paragraph({ spacing: { after: 0 }, children: [typeof paras === 'string' ? t(paras) : paras] })],
  });
}
function thcell(text, w) {
  return new TableCell({
    width: { size: w, type: WidthType.DXA },
    borders: { top: bThin, bottom: bBlue, left: bThin, right: bThin },
    shading: { type: ShadingType.CLEAR, fill: 'D0E4F0' },
    margins: { top: 80, bottom: 80, left: 100, right: 100 },
    children: [new Paragraph({ spacing: { after: 0 }, children: [tb(text)] })],
  });
}
function sp(text, opts = {}) {
  return new Paragraph({ spacing: { after: 0 }, children: [new TextRun({ text, font: 'Arial', size: 20, ...opts })] });
}

// ── Test result cell ──────────────────────────────────────────────────────────
function resCel(goal, nodes, path, w) {
  if (goal === 'No path found') {
    return tcell([
      new Paragraph({ spacing: { after: 0 }, children: [new TextRun({ text: 'No path found', font: 'Arial', size: 18, italics: true, color: 'AA0000' })] })
    ], { w });
  }
  return tcell([
    new Paragraph({ spacing: { after: 30 }, children: [new TextRun({ text: 'Goal: ' + goal, font: 'Arial', size: 18, bold: true })] }),
    new Paragraph({ spacing: { after: 30 }, children: [new TextRun({ text: nodes + ' nodes', font: 'Arial', size: 18, color: '555555' })] }),
    new Paragraph({ spacing: { after: 0 }, children: [new TextRun({ text: path, font: 'Courier New', size: 16, color: '1A1A8C' })] }),
  ], { w });
}

// ── Graph image cell (spans all columns) ──────────────────────────────────────
function graphRow(tcId, totalWidth) {
  const imgPath = path.join(__dirname, 'tests', 'graph_images', `${tcId}_all.png`);
  const imgData = fs.readFileSync(imgPath);
  // docx ImageRun transformation: width/height in pixels (rendered at 96dpi in Word)
  // Content width in inches = (totalWidth - 200) / 1440; pixels = inches * 96
  const widthPx  = Math.round((totalWidth - 200) / 1440 * 96);
  // Source image is 10:7 aspect ratio (figsize 10x7 in generate_graphs.py)
  const heightPx = Math.round(widthPx * 7 / 10);

  return new TableRow({
    children: [
      new TableCell({
        columnSpan: 8,
        width: { size: totalWidth, type: WidthType.DXA },
        borders: allThin,
        shading: { type: ShadingType.CLEAR, fill: 'F8F8F8' },
        margins: { top: 80, bottom: 80, left: 100, right: 100 },
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 0 },
          children: [new ImageRun({
            type: 'png',
            data: imgData,
            transformation: { width: widthPx, height: heightPx },
            altText: { title: tcId + ' graph', description: tcId + ' search paths', name: tcId },
          })],
        })],
      }),
    ],
  });
}

// ── Test data ─────────────────────────────────────────────────────────────────
const MC = Math.floor((CW - 900 - 1600) / 6); // ~1095 per method col
const tests = [
  { no:'TC01', desc:['Original sample','6 nodes, 2 destinations','Origin: 2, Goals: 5 and 4'],
    dfs:['5','7','2->1->3->5'], bfs:['4','6','2->1->4'], gbfs:['5','6','2->3->5'],
    as:['4','6','2->1->4'], cus1:['4','6','2->1->4'], cus2:['4','18','2->1->4'] },
  { no:'TC02', desc:['Origin equals destination','3 nodes','Origin: 1, Goal: 1'],
    dfs:['1','1','1'], bfs:['1','1','1'], gbfs:['1','1','1'],
    as:['1','1','1'], cus1:['1','1','1'], cus2:['1','1','1'] },
  { no:'TC03', desc:['No path exists','4 nodes, disconnected','Origin: 1, Goal: 4'],
    dfs:['No path found','',''], bfs:['No path found','',''], gbfs:['No path found','',''],
    as:['No path found','',''], cus1:['No path found','',''], cus2:['No path found','',''] },
  { no:'TC04', desc:['Minimal 2-node graph','Single direct edge','Origin: 1, Goal: 2'],
    dfs:['2','2','1->2'], bfs:['2','2','1->2'], gbfs:['2','2','1->2'],
    as:['2','2','1->2'], cus1:['2','2','1->2'], cus2:['2','2','1->2'] },
  { no:'TC05', desc:['GBFS vs A*','4 nodes, two paths','One cheap, one costly','Goal: 4'],
    dfs:['4','4','1->2->4'], bfs:['4','4','1->2->4'], gbfs:['4','4','1->2->4'],
    as:['4','5','1->3->4'], cus1:['4','5','1->2->4'], cus2:['4','7','1->3->4'] },
  { no:'TC06', desc:['Multiple destinations','6 nodes','Goals: 2, 3, 4'],
    dfs:['2','6','1->2'], bfs:['2','6','1->2'], gbfs:['2','6','1->2'],
    as:['4','6','1->4'], cus1:['2','2','1->2'], cus2:['4','9','1->4'] },
  { no:'TC07', desc:['Linear chain','5 nodes, one path','Goal: 5'],
    dfs:['5','5','1->2->3->4->5'], bfs:['5','5','1->2->3->4->5'], gbfs:['5','5','1->2->3->4->5'],
    as:['5','5','1->2->3->4->5'], cus1:['5','11','1->2->3->4->5'], cus2:['5','5','1->2->3->4->5'] },
  { no:'TC08', desc:['Directed edges','5 nodes, direction matters','Goal: 5'],
    dfs:['5','5','1->2->3->5'], bfs:['5','5','1->2->3->5'], gbfs:['5','5','1->2->3->5'],
    as:['5','5','1->2->3->5'], cus1:['5','8','1->2->3->5'], cus2:['5','8','1->2->3->5'] },
  { no:'TC09', desc:['Dense graph','6 nodes, many edges','Goal: 6'],
    dfs:['6','11','1->2->3->5->6'], bfs:['6','6','1->2->6'], gbfs:['6','8','1->2->6'],
    as:['6','6','1->2->6'], cus1:['6','9','1->2->6'], cus2:['6','18','1->2->6'] },
  { no:'TC10', desc:['Large 10-node graph','Multiple branching paths','Goal: 10'],
    dfs:['10','10','1->2->4->6->8->10'], bfs:['10','10','1->2->4->7->10'], gbfs:['10','9','1->2->4->7->10'],
    as:['10','9','1->2->4->7->10'], cus1:['10','30','1->2->4->7->10'], cus2:['10','54','1->2->4->7->10'] },
  { no:'TC11', desc:['Star topology','Hub connects to all nodes','Goal: 6'],
    dfs:['6','6','1->6'], bfs:['6','6','1->6'], gbfs:['6','6','1->6'],
    as:['6','6','1->6'], cus1:['6','6','1->6'], cus2:['6','11','1->6'] },
  { no:'TC12', desc:['Deep goal node','9 nodes, goal far from origin','Goal: 9'],
    dfs:['9','11','1->2->4->5->6->7->8->9'], bfs:['9','9','1->3->6->7->9'], gbfs:['9','8','1->3->6->7->9'],
    as:['9','9','1->3->6->7->9'], cus1:['9','30','1->3->6->7->9'], cus2:['9','51','1->3->6->7->9'] },
  { no:'TC13', desc:['Tiebreaking test','5 nodes, two equal-cost paths','Goal: 5'],
    dfs:['5','5','1->2->5'], bfs:['5','5','1->2->5'], gbfs:['5','5','1->2->5'],
    as:['5','5','1->2->5'], cus1:['5','6','1->2->5'], cus2:['5','12','1->2->5'] },
  { no:'TC14', desc:['Hop count vs edge cost','4 nodes','Goal: 2'],
    dfs:['2','3','1->2'], bfs:['2','3','1->2'], gbfs:['2','3','1->2'],
    as:['2','3','1->2'], cus1:['2','2','1->2'], cus2:['2','2','1->2'] },
  { no:'TC15', desc:['Partial reachability','5 nodes, dest 4 unreachable','Goals: 3, 4, 5'],
    dfs:['3','4','1->2->3'], bfs:['3','4','1->2->3'], gbfs:['3','4','1->2->3'],
    as:['3','4','1->2->3'], cus1:['3','4','1->2->3'], cus2:['3','4','1->2->3'] },
];

function makeTcRows(tc) {
  // Row 1: TC number + scenario description spanning all 8 cols
  const titleRow = new TableRow({ children: [
    new TableCell({
      columnSpan: 8,
      width: { size: CW, type: WidthType.DXA },
      borders: { top: { style: BorderStyle.SINGLE, size: 6, color: '2E4057' }, bottom: bThin, left: bThin, right: bThin },
      shading: { type: ShadingType.CLEAR, fill: 'EAF2FB' },
      margins: { top: 80, bottom: 80, left: 100, right: 100 },
      children: [new Paragraph({ spacing: { after: 0 }, children: [
        new TextRun({ text: tc.no + ': ', font: 'Arial', size: 22, bold: true, color: '2E4057' }),
        new TextRun({ text: tc.desc[0], font: 'Arial', size: 22, bold: true }),
        new TextRun({ text: '  |  ' + tc.desc.slice(1).join('  |  '), font: 'Arial', size: 20, color: '555555' }),
      ]})],
    }),
  ]});

  // Row 2: graph image spanning all 8 cols
  const imgRow = graphRow(tc.no, CW);

  // Row 3: result cells
  const resRow = new TableRow({ children: [
    tcell([new Paragraph({ spacing:{after:0}, children:[new TextRun({text:'Results', font:'Arial', size:18, bold:true, color:'555555'})] })], { w: 900 }),
    tcell([new Paragraph({ spacing:{after:0}, children:[new TextRun({text:'', font:'Arial', size:18})] })], { w: 1600 }),
    resCel(tc.dfs[0], tc.dfs[1], tc.dfs[2], MC),
    resCel(tc.bfs[0], tc.bfs[1], tc.bfs[2], MC),
    resCel(tc.gbfs[0], tc.gbfs[1], tc.gbfs[2], MC),
    resCel(tc.as[0], tc.as[1], tc.as[2], MC),
    resCel(tc.cus1[0], tc.cus1[1], tc.cus1[2], MC),
    resCel(tc.cus2[0], tc.cus2[1], tc.cus2[2], MC),
  ]});

  return [titleRow, imgRow, resRow];
}

const testTable = new Table({
  width: { size: CW, type: WidthType.DXA },
  columnWidths: [900, 1600, MC, MC, MC, MC, MC, MC],
  rows: [
    new TableRow({
      tableHeader: true,
      children: [
        thcell('TC', 900), thcell('Scenario / Graph', 1600),
        thcell('DFS', MC), thcell('BFS', MC),
        thcell('GBFS', MC), thcell('AS', MC), thcell('CUS1', MC), thcell('CUS2', MC),
      ]
    }),
    ...tests.flatMap(makeTcRows),
  ],
});

// ── Nodes created comparison table ───────────────────────────────────────────
const NC = Math.floor(CW / 8); // 8 equal cols
const nodesTable = new Table({
  width: { size: CW, type: WidthType.DXA },
  columnWidths: [NC, NC, NC, NC, NC, NC, NC, NC],
  rows: [
    new TableRow({
      tableHeader: true,
      children: ['TC', 'DFS', 'BFS', 'GBFS', 'AS', 'CUS1', 'CUS2', 'Notes'].map(h => thcell(h, NC)),
    }),
    ...[
      ['TC01','7','6','6','6','6','18','GBFS/AS/CUS1 tied'],
      ['TC05','4','4','4','5','5','7','A*/CUS2 explore more for optimality'],
      ['TC07','5','5','5','5','11','5','IDDFS re-expands nodes'],
      ['TC09','11','6','8','6','9','18','DFS goes deep; IDA* re-expands'],
      ['TC10','10','10','9','9','30','54','IDDFS and IDA* grow steeply'],
      ['TC12','11','9','8','9','30','51','Heuristic helps GBFS most'],
    ].map(row => new TableRow({ children: row.map((v, i) => {
      const bold = i === 0;
      return tcell([new Paragraph({ spacing:{after:0}, children:[new TextRun({ text:v, font:'Arial', size:20, bold })] })], { w: NC });
    })})),
  ],
});

// ── Cover page ────────────────────────────────────────────────────────────────
const cover = [
  bl(), bl(), bl(),
  para('COS30019 Introduction to Artificial Intelligence', { bold:true, size:28, after:160, align:AlignmentType.CENTER }),
  para('Assignment 2 Part A', { bold:true, size:24, after:80, align:AlignmentType.CENTER }),
  para('Tree-Based Search Report', { size:24, after:400, align:AlignmentType.CENTER }),
  para('Swinburne University of Technology', { size:22, after:80, align:AlignmentType.CENTER }),
  para('Semester 1, 2026', { size:22, after:400, align:AlignmentType.CENTER }),
  new Table({
    width: { size: CW, type: WidthType.DXA },
    columnWidths: [Math.floor(CW*0.35), Math.floor(CW*0.35), Math.floor(CW*0.3)],
    rows: [
      new TableRow({ children: [
        thcell('Full Name', Math.floor(CW*0.35)),
        thcell('Student ID', Math.floor(CW*0.35)),
        thcell('Contribution', Math.floor(CW*0.3)),
      ]}),
      ...['[Name 1]','[Name 2]','[Name 3]','[Name 4]'].map((name, i) =>
        new TableRow({ children: [
          tcell([sp(name)], { w: Math.floor(CW*0.35) }),
          tcell([sp('[Student ID]')], { w: Math.floor(CW*0.35) }),
          tcell([sp(i===0?'GBFS, A*, CUS1, Introduction, Testing, Insights':'[To be filled]')], { w: Math.floor(CW*0.3) }),
        ]})
      ),
    ],
  }),
  bl(), bl(),
  para('Statement of Contribution', { bold:true, size:22, after:100 }),
  para('All group members contributed to this assignment. Specific responsibilities are listed in the table above. Each member reviewed the work produced by others before submission. By signing below, all members confirm the accuracy of the contribution statement.', { size:22, after:200 }),
  para('Signatures: ______________________    ______________________    ______________________    ______________________', { size:20, after:80 }),
  pb(),
];

// ── TOC ───────────────────────────────────────────────────────────────────────
const toc = [
  new TableOfContents('Table of Contents', {
    hyperlink: true, headingStyleRange: '1-3',
  }),
  pb(),
];

// ── 1. Instructions ───────────────────────────────────────────────────────────
const instructions = [
  h1('1. Instructions'),
  para('The program is a command-line Python application. No installation beyond Python 3 is required.'),
  h2('1.1 Running a Search'),
  para('From the project directory, run:'),
  code('python search.py <filename> <method>'),
  para('Where:'),
  bul('filename is the path to a problem text file (e.g., tests/test_cases/PathFinder-test-1.txt)'),
  bul('method is one of: DFS, BFS, GBFS, AS, CUS1, CUS2 (case-insensitive)'),
  bl(),
  para('Example:'),
  code('python search.py tests/test_cases/PathFinder-test-1.txt AS'),
  h2('1.2 Output Format'),
  para('When a path is found, the program prints three lines:'),
  code('<filename> <method>'),
  code('<goal_node> <nodes_created>'),
  code('<path>'),
  para('When no path exists:'),
  code('<filename> <method>'),
  code('No path found'),
  h2('1.3 Running All Tests'),
  para('To run the full automated test suite against all 15 test cases:'),
  code('python tests/run_tests.py'),
  para('The test runner reports pass or fail for each (test case, method) pair and prints a summary at the end.'),
  pb(),
];

// ── 2. Introduction ───────────────────────────────────────────────────────────
const introduction = [
  h1('2. Introduction'),
  h2('2.1 The Route Finding Problem'),
  para('Route finding is one of the most widely studied problems in artificial intelligence. The task is to find a path from a starting location to a destination within a graph, minimising some measure of cost such as distance, time or number of steps. Applications range from GPS navigation and logistics to game AI and robotic motion planning.'),
  para('In this assignment, the graph is a directed, weighted graph embedded in two-dimensional space. Each node has a unique integer identifier and a coordinate position (x, y). Directed edges connect pairs of nodes and carry a positive traversal cost. The agent begins at an origin node and must reach any one of a set of destination nodes. Multiple destinations are allowed, and the agent succeeds as soon as it reaches the first one.'),
  para('Edge direction matters: the existence of an edge from node A to node B does not imply an edge from B to A. This makes the problem more realistic and ensures that some paths may be blocked in one direction.'),
  h2('2.2 Graph and Tree Concepts'),
  para('A graph is a collection of nodes (also called vertices) connected by edges. A directed graph restricts traversal to the specified direction of each edge. A weighted graph assigns a numerical cost to each edge, representing the expense of traversal.'),
  para('A search tree is a tree built incrementally during the search process. The root node corresponds to the origin. Each child of a node in the tree represents a state reachable from the parent by traversing one edge. Unlike the underlying graph, the search tree can contain the same graph node multiple times, once for each distinct path that leads to it.'),
  para('The frontier (also called the open list) holds all nodes that have been generated but not yet expanded. The explored set (or closed list) records nodes that have been fully expanded. Together, these structures control which nodes are visited and in what order.'),
  h2('2.3 Search Algorithms Overview'),
  para('Six tree-based search algorithms are implemented in this project. Two are uninformed, meaning they use only the graph structure to guide the search. Two are informed, using a heuristic estimate of the distance to the goal. Two are custom strategies, one uninformed and one informed, chosen to complement the standard methods.'),
  para('All six algorithms share the same interface and output format. Tiebreaking follows a consistent rule across all methods: when two nodes have equal priority, the one with the smaller node identifier is expanded first. When node identifiers are also equal (two paths reaching the same node), the node added to the frontier earlier is expanded first.'),
  new Table({
    width: { size: CW, type: WidthType.DXA },
    columnWidths: [Math.floor(CW*0.12), Math.floor(CW*0.18), Math.floor(CW*0.12), Math.floor(CW*0.12), Math.floor(CW*0.46)],
    rows: [
      new TableRow({ tableHeader: true, children: [
        thcell('Method', Math.floor(CW*0.12)),
        thcell('Name', Math.floor(CW*0.18)),
        thcell('Type', Math.floor(CW*0.12)),
        thcell('Optimal', Math.floor(CW*0.12)),
        thcell('Brief Description', Math.floor(CW*0.46)),
      ]}),
      ...[
        ['DFS','Depth-First Search','Uninformed','No','Explores as deep as possible along each branch before backtracking.'],
        ['BFS','Breadth-First Search','Uninformed','By hops','Explores all nodes at each depth level before moving deeper.'],
        ['GBFS','Greedy Best-First','Informed','No','Expands the node with the lowest heuristic value h(n).'],
        ['AS','A* Search','Informed','Yes','Expands the node with the lowest f(n) = g(n) + h(n).'],
        ['CUS1','IDDFS','Uninformed','By hops','Iterative deepening combines DFS space use with BFS completeness.'],
        ['CUS2','IDA*','Informed','Yes','Iterative deepening with A* f-bound pruning for optimal cost paths.'],
      ].map(row => new TableRow({ children: row.map((v, i) => {
        const w = [Math.floor(CW*0.12), Math.floor(CW*0.18), Math.floor(CW*0.12), Math.floor(CW*0.12), Math.floor(CW*0.46)][i];
        return tcell([new Paragraph({ spacing:{after:0}, children:[new TextRun({ text:v, font:'Arial', size:20 })] })], { w });
      })})),
    ],
  }),
  bl(),
  para('Table 1: Summary of implemented search algorithms.', { size:20, italics:true }),
  pb(),
];

// ── 3. Algorithm Implementations ─────────────────────────────────────────────
const algorithms = [
  h1('3. Algorithm Implementations'),

  // 3.1 DFS
  h2('3.1 Depth-First Search (DFS)'),
  para('[To be completed by teammate.]', { italics:true, color:'888888' }),
  bl(),

  // 3.2 BFS
  h2('3.2 Breadth-First Search (BFS)'),
  para('[To be completed by teammate.]', { italics:true, color:'888888' }),
  bl(),

  // 3.3 GBFS
  h2('3.3 Greedy Best-First Search (GBFS)'),
  h3('Overview'),
  para('Greedy Best-First Search is an informed search strategy that selects the next node to expand based entirely on a heuristic estimate of the distance remaining to the goal. It does not account for the cost already paid to reach the current node. The evaluation function is:'),
  mp([t('f(n) = h(n)'), t(' where '), ti('h(n)'), t(' is the Euclidean distance from node n to the nearest destination.')], { indent:720, after:160 }),
  para('The algorithm maintains a priority queue sorted by h(n) in ascending order, always expanding the node that appears geometrically closest to the goal. Because it ignores path cost, GBFS can be misled by nodes that look close to the goal but require an expensive route to reach.'),
  h3('Heuristic Function'),
  para('Euclidean (straight-line) distance is used as the heuristic. For a node at coordinates (x1, y1) and a destination at (x2, y2), the heuristic value is the square root of (x1 - x2) squared plus (y1 - y2) squared. When multiple destinations exist, h(n) is the minimum over all destination distances. This ensures the heuristic measures the distance to the nearest goal, which is consistent with the objective of reaching any one destination.'),
  h3('Tiebreaking'),
  para('The priority queue uses a three-element tuple as its key: (h value, node ID, insertion counter). Equal heuristic values are resolved by ascending node ID. Equal node IDs on different branches are resolved by chronological insertion order. This satisfies both tiebreaking rules specified in the assignment.'),
  h3('Properties'),
  new Table({
    width: { size: Math.floor(CW*0.7), type: WidthType.DXA },
    columnWidths: [Math.floor(CW*0.25), Math.floor(CW*0.45)],
    rows: [
      new TableRow({ tableHeader:true, children:[thcell('Property', Math.floor(CW*0.25)), thcell('Value', Math.floor(CW*0.45))] }),
      ...[
        ['Complete','Yes, on finite graphs with an explored set'],
        ['Optimal','No, may return a higher-cost path'],
        ['Time complexity','O(b^m) worst case'],
        ['Space complexity','O(b^m), all generated nodes are stored'],
        ['Heuristic','Euclidean distance to nearest destination'],
      ].map(([k,v]) => new TableRow({ children: [
        tcell([sp(k,{bold:true})], {w:Math.floor(CW*0.25)}),
        tcell([sp(v)], {w:Math.floor(CW*0.45)}),
      ]})),
    ],
  }),
  bl(),
  para('Table 2: GBFS algorithm properties.', { size:20, italics:true }),
  para('Key limitation: GBFS can return a suboptimal path because it ignores g(n). In test case TC05, GBFS reaches node 4 via the path 1 to 2 to 4 at a total edge cost of 11. A*, by contrast, finds the path 1 to 3 to 4 at a total cost of 2. This demonstrates that heuristic guidance alone is not sufficient for optimal search.'),
  bl(),

  // 3.4 A*
  h2('3.4 A* Search (AS)'),
  h3('Overview'),
  para('A* Search is an informed search algorithm that guarantees finding the optimal (lowest total cost) path, provided the heuristic function is admissible. It evaluates nodes using the combined function:'),
  mp([t('f(n) = g(n) + h(n)')], { indent:720, after:100 }),
  mp([ti('g(n)'), t(' is the exact cumulative edge cost from the origin to node n.')], { indent:720, after:80 }),
  mp([ti('h(n)'), t(' is the Euclidean distance from node n to the nearest destination.')], { indent:720, after:160 }),
  para('By including g(n), A* weighs both how expensive the current path has been and how far the goal appears to be. Nodes with a low combined cost are expanded first, which means A* explores fewer irrelevant nodes than GBFS while still being guided by the heuristic toward the goal.'),
  h3('Admissibility of the Heuristic'),
  para('A heuristic is admissible if it never overestimates the true remaining cost. The Euclidean distance satisfies this requirement because the straight-line distance between two points is always less than or equal to any path connecting them along actual edges. Since edge costs in this problem represent physical distances on a 2D coordinate grid, h(n) is always a lower bound on the true cost.'),
  para('Because the heuristic is admissible, A* is guaranteed to return an optimal path. The first time A* expands a node, it has found the cheapest possible path to that node.'),
  h3('Cost Table'),
  para('The implementation maintains a g_cost table mapping each node to the lowest known cumulative cost from the origin. When a node is about to be pushed to the frontier, its tentative g value is compared to g_cost. It is only pushed if the new path is strictly cheaper, avoiding redundant entries in the frontier.'),
  h3('Properties'),
  new Table({
    width: { size: Math.floor(CW*0.7), type: WidthType.DXA },
    columnWidths: [Math.floor(CW*0.25), Math.floor(CW*0.45)],
    rows: [
      new TableRow({ tableHeader:true, children:[thcell('Property', Math.floor(CW*0.25)), thcell('Value', Math.floor(CW*0.45))] }),
      ...[
        ['Complete','Yes'],
        ['Optimal','Yes, with admissible heuristic'],
        ['Time complexity','O(b^d) where d is depth of optimal solution'],
        ['Space complexity','O(b^d), all generated nodes are stored'],
        ['Heuristic','Euclidean distance (admissible)'],
      ].map(([k,v]) => new TableRow({ children: [
        tcell([sp(k,{bold:true})], {w:Math.floor(CW*0.25)}),
        tcell([sp(v)], {w:Math.floor(CW*0.45)}),
      ]})),
    ],
  }),
  bl(),
  para('Table 3: A* algorithm properties.', { size:20, italics:true }),
  para('Key difference from GBFS: In TC06, GBFS, DFS and BFS all reach destination 2 because it appears first in the search. A* correctly identifies that destination 4 is reachable at a lower total cost via the direct edge from node 1, and returns that instead.'),
  bl(),

  // 3.5 CUS1
  h2('3.5 Custom Strategy 1: Iterative Deepening Depth-First Search (IDDFS)'),
  h3('Motivation and Design Choice'),
  para('The assignment requires CUS1 to be an uninformed method that finds a path to the goal. Iterative Deepening Depth-First Search was chosen because it is strictly superior to both DFS and BFS for this problem in terms of completeness and memory use.'),
  para('Standard DFS is not complete on graphs with cycles unless a visited set is used, and it does not guarantee finding the shallowest solution. BFS is complete and finds the shallowest path, but requires O(b^d) memory to hold the entire frontier, which grows exponentially with depth. IDDFS achieves the same shallowest-path guarantee as BFS while using only O(b times d) memory, the same as DFS.'),
  h3('How IDDFS Works'),
  para('The algorithm performs successive depth-limited DFS iterations. In the first iteration, it explores all nodes reachable within one hop from the origin. If no goal is found, it tries two hops, then three, and so on. Each iteration starts fresh from the origin.'),
  para('The first solution found is always the shallowest one, because all paths of length d are explored before any path of length d + 1. This is exactly the same guarantee as BFS.'),
  h3('Node Re-expansion'),
  para('IDDFS re-expands nodes across iterations. A node at depth 3 is created once in the depth-3 iteration and again in the depth-4 iteration. The total number of nodes created is therefore larger than for BFS on the same problem. However, because node counts grow exponentially with depth, the overhead from re-expanding upper levels adds only a constant factor of approximately b divided by (b minus 1) over the total work.'),
  para('The node count reported for CUS1 accumulates all node creations across every iteration, reflecting the true cost of the algorithm.'),
  h3('Cycle Detection'),
  para('Cycle detection uses a per-iteration path set. Each recursive call checks whether a neighbour already appears on the current path from the origin. If it does, the neighbour is skipped. This prevents infinite loops on cyclic graphs while still allowing nodes to appear on different branches or be revisited in later depth iterations.'),
  h3('Properties'),
  new Table({
    width: { size: Math.floor(CW*0.7), type: WidthType.DXA },
    columnWidths: [Math.floor(CW*0.25), Math.floor(CW*0.45)],
    rows: [
      new TableRow({ tableHeader:true, children:[thcell('Property', Math.floor(CW*0.25)), thcell('Value', Math.floor(CW*0.45))] }),
      ...[
        ['Complete','Yes, on finite graphs'],
        ['Optimal','Yes, by hop count (fewest edges)'],
        ['Cost-optimal','No, does not minimise total edge cost'],
        ['Time complexity','O(b^d), same asymptotic as BFS'],
        ['Space complexity','O(b x d), far better than BFS'],
        ['Informed','No, uses only graph structure'],
      ].map(([k,v]) => new TableRow({ children: [
        tcell([sp(k,{bold:true})], {w:Math.floor(CW*0.25)}),
        tcell([sp(v)], {w:Math.floor(CW*0.45)}),
      ]})),
    ],
  }),
  bl(),
  para('Table 4: CUS1 (IDDFS) algorithm properties.', { size:20, italics:true }),
  para('In TC07 (linear chain), CUS1 created 11 nodes compared to 5 for DFS and BFS. This reflects the re-expansion overhead: in iterations 1 through 4, CUS1 re-explores the shorter prefixes of the chain before reaching the goal at depth 4. Despite the extra work, CUS1 uses the same O(d) stack memory as DFS throughout.'),
  bl(),

  // 3.6 CUS2
  h2('3.6 Custom Strategy 2: Iterative Deepening A* (IDA*)'),
  para('[To be completed by teammate.]', { italics:true, color:'888888' }),
  pb(),
];

// ── 4. Features, Bugs and Missing ────────────────────────────────────────────
const features = [
  h1('4. Features, Bugs and Missing Features'),
  h2('4.1 Implemented Features'),
  bul('All six required search methods: DFS, BFS, GBFS, AS, CUS1 (IDDFS) and CUS2 (IDA*)'),
  bul('Command-line interface accepting filename and method as arguments'),
  bul('Parser for the problem file format including directed weighted edges and multiple destinations'),
  bul('Correct output format: filename, method, goal node, nodes created and path'),
  bul('Tiebreaking by ascending node ID and chronological insertion order across all methods'),
  bul('Automated test runner with 15 test cases covering a wide range of scenarios'),
  bul('Graceful handling of unreachable goals, printing "No path found"'),
  h2('4.2 Known Bugs'),
  para('No known bugs at time of submission. All 90 test assertions pass (15 test cases times 6 methods).'),
  h2('4.3 Missing Features'),
  para('All required features from the assignment specification have been implemented. The program correctly supports the three command-line formats described in the specification.'),
  pb(),
];

// ── 5. Testing ────────────────────────────────────────────────────────────────
const testing = [
  h1('5. Testing'),
  h2('5.1 Test Strategy'),
  para('Testing was conducted automatically using a test runner script located at tests/run_tests.py. The runner executes every test case file in the tests/test_cases/ directory against all six methods and compares the output to a predefined expected result. A test passes if and only if both the goal node and the complete path string match exactly.'),
  para('Fifteen test cases were created to cover the following categories of scenarios:'),
  bul('Trivial cases: origin already at the destination (TC02), minimal two-node graph (TC04)'),
  bul('Failure cases: no path exists due to disconnected graph (TC03)'),
  bul('Algorithm contrast: scenarios where different algorithms return different paths or goals (TC05, TC06)'),
  bul('Structural variety: linear chains (TC07), directed graphs (TC08), dense graphs (TC09), star topology (TC11)'),
  bul('Scale: a 10-node graph to test scalability (TC10), a deep goal far from origin (TC12)'),
  bul('Correctness properties: tiebreaking validation (TC13), hop vs cost trade-off (TC14), partial reachability (TC15)'),
  para('All 90 test assertions passed (15 test cases times 6 methods).'),
  h2('5.2 Test Case Results'),
  para('Table 5 shows the results of running all 15 test cases against all six methods. For each cell, the goal node reached, number of nodes created and the path taken are shown.'),
  bl(),
  testTable,
  bl(),
  para('Table 5: Complete test results across all 15 test cases and 6 methods.', { size:20, italics:true }),
  pb(),
];

// ── 6. Insights ───────────────────────────────────────────────────────────────
const insights = [
  h1('6. Insights'),
  h2('6.1 Optimality'),
  para('The test data clearly separates the algorithms that find optimal cost paths from those that do not. A* and CUS2 (IDA*) consistently return the minimum cost paths. GBFS, DFS, BFS and CUS1 do not guarantee cost optimality.'),
  para('Test case TC05 illustrates this most starkly. Two paths exist from node 1 to node 4: the direct path 1 to 2 to 4 costs 11, while the path 1 to 3 to 4 costs only 2. GBFS chooses node 2 first because it appears slightly closer to the goal by heuristic distance, then proceeds to the expensive edge. A* and CUS2 correctly identify the cheaper path via node 3 by keeping track of the accumulated cost g(n). DFS and BFS also miss the optimal path because they have no cost awareness at all.'),
  para('In TC06, the three destinations are nodes 2, 3 and 4. DFS, BFS and GBFS stop at node 2, the first destination they reach. A* and CUS2 continue to evaluate whether another destination can be reached at lower cost, and correctly choose node 4 because it is directly reachable at a lower total f value.'),
  h2('6.2 Nodes Created (Memory and Effort)'),
  para('Table 6 compares nodes created across selected test cases. This is the most informative measure of algorithmic effort.'),
  bl(),
  nodesTable,
  bl(),
  para('Table 6: Nodes created comparison across selected test cases.', { size:20, italics:true }),
  para('Several patterns emerge from the data. DFS creates fewer nodes than BFS in graphs where the goal lies deep on the first branch explored (TC01: 7 vs 6, TC12: 11 vs 9). In dense graphs (TC09), DFS created 11 nodes because it followed a longer branch of depth 4 before finding the goal, while BFS found it in 2 hops at 6 nodes.'),
  para('GBFS generally creates a similar number of nodes to A* but occasionally fewer, because it ignores g(n) and commits to apparently promising nodes more aggressively. In TC10, both created 9 nodes and found the same path. In TC09, GBFS created 8 to A*\'s 6.'),
  para('CUS1 (IDDFS) creates significantly more nodes than BFS in larger graphs. In TC10, BFS created 10 nodes while CUS1 created 30. This reflects re-expansion across multiple depth iterations. The trade-off is memory: BFS must hold all frontier nodes in memory simultaneously, while IDDFS only holds a single path stack.'),
  para('CUS2 (IDA*) shows the most extreme node creation counts due to re-expansion with an f-bound that tightens over multiple iterations. In TC12, IDA* created 51 nodes compared to 9 for A*. For large or deep search spaces, this overhead grows substantially.'),
  h2('6.3 GBFS Insights'),
  para('GBFS is fast and simple, and works well when the heuristic closely reflects the actual cost. In TC11 (star topology), TC04 (two nodes) and TC07 (linear chain), GBFS performs identically to A*. However, as TC05 shows, GBFS can be significantly misled. The practical recommendation is to use GBFS when speed is critical and suboptimal solutions are acceptable.'),
  h2('6.4 A* Insights'),
  para('A* provides the best balance between speed and optimality among the six methods. It consistently finds the lowest cost paths while creating a relatively small number of nodes. The g_cost pruning mechanism in this implementation prevents the frontier from growing unnecessarily: only better paths to a node are ever pushed. In all test cases, A* found optimal paths and its node counts were comparable to or better than BFS.'),
  h2('6.5 CUS1 (IDDFS) Insights'),
  para('IDDFS is a practical uninformed algorithm for memory-constrained environments. It produces the same hop-optimal results as BFS at a fraction of the memory cost. The node creation overhead is predictable and bounded by a constant factor. For this assignment\'s graphs, CUS1 consistently found the same goals and paths as BFS (with the same number of hops), confirming its theoretical guarantees hold in practice.'),
  h2('6.6 Algorithm Comparison Summary'),
  new Table({
    width: { size: CW, type: WidthType.DXA },
    columnWidths: [
      Math.floor(CW*0.13), Math.floor(CW*0.13), Math.floor(CW*0.13),
      Math.floor(CW*0.13), Math.floor(CW*0.14), Math.floor(CW*0.34),
    ],
    rows: [
      new TableRow({ tableHeader:true, children: [
        thcell('Method', Math.floor(CW*0.13)),
        thcell('Cost-Optimal', Math.floor(CW*0.13)),
        thcell('Hop-Optimal', Math.floor(CW*0.13)),
        thcell('Memory', Math.floor(CW*0.13)),
        thcell('Speed', Math.floor(CW*0.14)),
        thcell('Best Use Case', Math.floor(CW*0.34)),
      ]}),
      ...[
        ['DFS','No','No','Low','Fast on lucky graphs','Quick any-path search with memory constraints'],
        ['BFS','No','Yes','High','Moderate','Finding fewest-hop path, small graphs'],
        ['GBFS','No','No','Moderate','Fastest guided','Speed over optimality, good heuristics'],
        ['A*','Yes','Yes','Moderate','Good','Optimal cost path, general purpose'],
        ['CUS1','No','Yes','Very low','Slow (re-expand)','Hop-optimal search with minimal memory'],
        ['CUS2','Yes','Yes','Very low','Slowest','Optimal cost, very large state spaces'],
      ].map(row => new TableRow({ children: row.map((v, i) => {
        const ws = [Math.floor(CW*0.13), Math.floor(CW*0.13), Math.floor(CW*0.13),
                    Math.floor(CW*0.13), Math.floor(CW*0.14), Math.floor(CW*0.34)];
        return tcell([new Paragraph({ spacing:{after:0}, children:[new TextRun({ text:v, font:'Arial', size:20, bold: i===0 })] })], { w: ws[i] });
      })})),
    ],
  }),
  bl(),
  para('Table 7: Algorithm comparison summary.', { size:20, italics:true }),
  pb(),
];

// ── 7. Research ───────────────────────────────────────────────────────────────
const research = [
  h1('7. Research'),
  h2('7.1 Visiting All Destinations via the Shortest Path'),
  para('The assignment suggests investigating whether the program can be extended to visit all destination nodes using the shortest overall path, rather than stopping at the first destination found. This is a significantly harder problem known as the shortest Hamiltonian path problem on a subset of nodes, which is NP-hard in the general case.'),
  para('One practical approach for small numbers of destinations is to use A* with a modified heuristic that accounts for all remaining unvisited destinations. The state space is expanded to include the set of already-visited destinations as part of each node. The heuristic becomes the minimum spanning tree cost over the remaining destinations plus the distance to the nearest unvisited one.'),
  para('For the graphs in this assignment, where the number of destinations is typically small (two or three), this approach would be feasible. A brute-force approach trying all permutations of destination visit orders and selecting the one with minimum total path cost would also work for up to five or six destinations.'),
  para('Implementing this extension is identified as a potential future improvement but is outside the scope of the current submission.'),
  pb(),
];

// ── 8. Conclusion ─────────────────────────────────────────────────────────────
const conclusion = [
  h1('8. Conclusion'),
  para('This project implemented six tree-based search algorithms for the route finding problem on directed, weighted 2D graphs. The results from 15 test cases provide clear evidence of the trade-offs between the algorithms.'),
  para('For problems where finding the optimal cost path is the priority, A* is the recommended algorithm. It is complete, optimal with an admissible heuristic, and creates a manageable number of nodes in practice. CUS2 (IDA*) achieves the same optimality guarantee with a much smaller memory footprint, at the cost of significantly more node re-expansions.'),
  para('For problems where any valid path is acceptable and speed matters more than cost, GBFS performs well. It uses the heuristic to reach the goal quickly and creates fewer nodes than A* in most cases. However, as TC05 demonstrates, it can commit to a costly path that a cost-aware algorithm would avoid.'),
  para('BFS and CUS1 (IDDFS) are the best choices when hop-count minimisation is the goal rather than edge cost. IDDFS is preferred in memory-constrained settings because it achieves the same completeness and hop-optimality as BFS while using only linear stack space.'),
  para('DFS is the weakest general-purpose algorithm in this problem class because it provides no optimality guarantee and can explore long irrelevant branches before finding a solution. It is most useful when any path is acceptable and the graph is structured so that the first branch explored likely contains the goal.'),
  para('The main improvement opportunity is extending the program to find the minimum cost path that visits all destination nodes, which would require a more sophisticated multi-goal search strategy such as TSP-style dynamic programming or branch-and-bound.'),
  pb(),
];

// ── 9. Acknowledgements ───────────────────────────────────────────────────────
const acknowledgements = [
  h1('9. Acknowledgements and Resources'),
  bul('Russell, S. and Norvig, P. (2021). Artificial Intelligence: A Modern Approach, 4th Edition. Pearson. Used as the primary reference for all search algorithm descriptions and theoretical properties, including IDDFS (Section 3.4.4) and IDA* (Section 3.5.3).'),
  bul('Python heapq documentation (https://docs.python.org/3/library/heapq.html). Used to understand min-heap behaviour and tie-breaking in the priority queue implementations for GBFS and A*.'),
  bul('COS30019 lecture slides, Swinburne University, Semester 1 2026. Provided the problem specification, tiebreaking rules, and the format of the input files and expected output.'),
  bul('Korf, R. E. (1985). Depth-first iterative-deepening: An optimal admissible tree search. Artificial Intelligence, 27(1), 97-109. Original paper describing the IDA* algorithm used for CUS2.'),
  pb(),
];

// ── 10. References ────────────────────────────────────────────────────────────
const references = [
  h1('10. References'),
  para('[1] Russell, S. and Norvig, P. (2021). Artificial Intelligence: A Modern Approach, 4th ed. Pearson.'),
  para('[2] Korf, R. E. (1985). Depth-first iterative-deepening: An optimal admissible tree search. Artificial Intelligence, 27(1), pp. 97-109.'),
  para('[3] Python Software Foundation. heapq - Heap queue algorithm. Python 3 Documentation. Available at: https://docs.python.org/3/library/heapq.html'),
  para('[4] COS30019 Introduction to Artificial Intelligence, Lecture Slides, Swinburne University of Technology, 2026.'),
];

// ── Build document ────────────────────────────────────────────────────────────
const doc = new Document({
  numbering: {
    config: [
      { reference: 'bullets', levels: [{
        level: 0, format: LevelFormat.BULLET, text: '\u2022',
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } },
      }, {
        level: 1, format: LevelFormat.BULLET, text: '\u25e6',
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 1080, hanging: 360 } } },
      }] },
    ],
  },
  styles: {
    default: { document: { run: { font: 'Arial', size: 22 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 36, bold: true, font: 'Arial', color: '2E4057' },
        paragraph: { spacing: { before: 480, after: 200 }, outlineLevel: 0,
          border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: '2E4057', space: 1 } } } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 28, bold: true, font: 'Arial', color: '2E4057' },
        paragraph: { spacing: { before: 320, after: 160 }, outlineLevel: 1 } },
      { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 24, bold: true, font: 'Arial', color: '555555' },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 } },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: PW, height: PH },
        margin: { top: M, right: M, bottom: M, left: M },
      },
    },
    headers: {
      default: new Header({ children: [
        mp([
          t('COS30019 Assignment 2A', { size: 18, color: '555555' }),
          new TextRun({ text: '\t', font: 'Arial', size: 18 }),
          t('Tree-Based Search Report', { size: 18, color: '555555' }),
        ], { align: AlignmentType.LEFT }),
      ]}),
    },
    footers: {
      default: new Footer({ children: [
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 0 },
          border: { top: { style: BorderStyle.SINGLE, size: 2, color: 'CCCCCC', space: 1 } },
          children: [
            t('Page ', { size: 18, color: '555555' }),
            new TextRun({ children: [PageNumber.CURRENT], font: 'Arial', size: 18, color: '555555' }),
            t(' of ', { size: 18, color: '555555' }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], font: 'Arial', size: 18, color: '555555' }),
          ],
        }),
      ]}),
    },
    children: [
      ...cover,
      ...toc,
      ...instructions,
      ...introduction,
      ...algorithms,
      ...features,
      ...testing,
      ...insights,
      ...research,
      ...conclusion,
      ...acknowledgements,
      ...references,
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync('report_draft.docx', buf);
  console.log('Created report_draft.docx');
});
