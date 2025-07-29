const esprima = require('esprima');  // JS 解析器
const estraverse = require('estraverse');  // AST 遍历
const escodegen = require('escodegen');  // 代码生成

class JSTracer {
    // 分析代码生成基本块
    divideIntoBlocks(code) {
        const ast = esprima.parse(code);
        const blocks = [];
        let currentBlock = [];
        
        // 遍历 AST 识别基本块
        estraverse.traverse(ast, {
            enter: (node) => {
                if (this.isBlockStart(node)) {
                    if (currentBlock.length > 0) {
                        blocks.push(currentBlock);
                        currentBlock = [];
                    }
                }
                currentBlock.push(node);
            }
        });
        
        if (currentBlock.length > 0) {
            blocks.push(currentBlock);
        }
        
        return blocks;
    }

    // 在代码块前后插入监控代码
    instrument(code, functionName) {
        const blocks = this.divideIntoBlocks(code);
        let instrumentedCode = '';
        
        blocks.forEach((block, index) => {
            // 在块前插入变量监控
            instrumentedCode += `
                console.log('Block-${index} Start:');
                console.log(JSON.stringify(
                    Object.fromEntries(
                        Object.entries(this).filter(([k]) => !k.startsWith('_'))
                    )
                ));
            `;
            
            // 原始代码块
            instrumentedCode += escodegen.generate({
                type: 'Program',
                body: block
            });
            
            // 在块后插入变量监控
            instrumentedCode += `
                console.log('Block-${index} End:');
                console.log(JSON.stringify(
                    Object.fromEntries(
                        Object.entries(this).filter(([k]) => !k.startsWith('_'))
                    )
                ));
            `;
        });
        
        return instrumentedCode;
    }

    // 执行插桩后的代码
    executeAndTrace(code, functionName, testCase) {
        const instrumentedCode = this.instrument(code, functionName);
        
        // 使用 vm 模块在隔离环境中执行代码
        const vm = require('vm');
        const sandbox = {};
        vm.createContext(sandbox);
        
        try {
            vm.runInContext(instrumentedCode + '\n' + testCase, sandbox);
            return sandbox.output; // 收集执行输出
        } catch (error) {
            return `Execution Error: ${error.message}`;
        }
    }

    // 判断节点是否为块的开始
    isBlockStart(node) {
        return node.type === 'FunctionDeclaration' ||
               node.type === 'IfStatement' ||
               node.type === 'ForStatement' ||
               node.type === 'WhileStatement' ||
               node.type === 'DoWhileStatement';
    }
} 