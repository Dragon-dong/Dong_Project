// 语言资源文件
const i18n = {
    zh: {
        // 页面标题
        title: "跨模态内容生成系统",
        subtitle: "大模型增强版 - 文生图 · 图生文 · 动态叙事 · 风格控制",
        
        // 标签页
        textToImage: "文生图",
        imageToText: "图生文",
        dynamicNarrative: "动态叙事",
        styleTransfer: "风格迁移",
        
        // 文生图
        textToImageTitle: "文本生成图像",
        textPrompt: "描述文本",
        textPromptPlaceholder: "请输入图像描述，例如：一只可爱的猫在阳光下睡觉",
        imageStyle: "风格选择",
        customStyle: "自定义风格指令",
        customStylePlaceholder: "例如：赛博朋克风格+水墨画笔触",
        generateImage: "生成图像",
        clearImage: "清空",
        generating: "生成中，请稍候...",
        generationResult: "生成结果",
        
        // 图生文
        imageToTextTitle: "图像生成描述",
        uploadImage: "上传图像",
        uploadPlaceholder: "点击或拖拽图像到此处上传",
        uploadFormat: "支持 JPG、PNG、WebP 格式",
        generateText: "生成描述",
        clearText: "清空",
        
        // 动态叙事
        dynamicNarrativeTitle: "动态叙事生成",
        storyKeywords: "关键词",
        storyKeywordsPlaceholder: "请输入关键词，用逗号分隔，例如：冒险, 森林, 神秘生物",
        storyStyle: "故事风格",
        storyLength: "故事长度",
        storyStyleOptions: {
            fantasy: "奇幻",
            "sci-fi": "科幻",
            mystery: "悬疑",
            romance: "浪漫",
            adventure: "冒险"
        },
        storyLengthOptions: {
            short: "短篇（3-5个场景）",
            medium: "中篇（5-8个场景）",
            long: "长篇（8-12个场景）"
        },
        generateStory: "生成故事",
        clearStory: "清空",
        storyPreview: "故事预览",
        timelineEdit: "时间轴编辑",
        
        // 风格迁移
        styleTransferTitle: "风格迁移控制",
        uploadOriginalImage: "上传原始图像",
        styleInstruction: "风格指令",
        styleInstructionPlaceholder: "请输入风格指令，例如：将这幅画转换为梵高星空风格",
        transferStyle: "风格迁移",
        clearStyle: "清空",
        styleTransferResult: "风格迁移结果",
        
        // 智能助手
        smartAssistant: "智能助手",
        assistantGreeting: "你好！我是跨模态内容生成系统的智能助手。请问有什么可以帮助您的？",
        chatPlaceholder: "输入您的问题...",
        send: "发送",
        
        // 登录/注册
        loginRegister: "用户登录/注册",
        login: "登录",
        register: "注册",
        username: "用户名",
        password: "密码",
        email: "邮箱",
        confirmPassword: "确认密码",
        loginSuccess: "登录成功",
        registerSuccess: "注册成功，请登录",
        loginError: "用户名或密码错误",
        registerError: "注册失败，请重试",
        logout: "退出",
        
        // 风格预设
        stylePresets: [
            "写实风格",
            "卡通风格",
            "油画风格",
            "水彩风格",
            "赛博朋克",
            "中国风"
        ],
        
        // 提示信息
        pleaseEnterPrompt: "请输入描述文本",
        pleaseUploadImage: "请先上传图像",
        pleaseEnterKeywords: "请输入关键词",
        generationFailed: "生成失败，请检查后端服务是否运行",
        
        // 成功消息
        imageGenerated: "已为您生成图像：",
        textGenerated: "已为您生成图像描述",
        
        // 语言选择
        languages: {
            zh: "中文",
            en: "English",
            ja: "日本語"
        }
    },
    en: {
        // 页面标题
        title: "Cross-Modal Content Generation System",
        subtitle: "LLM Enhanced Version - Text to Image · Image to Text · Dynamic Narrative · Style Control",
        
        // 标签页
        textToImage: "Text to Image",
        imageToText: "Image to Text",
        dynamicNarrative: "Dynamic Narrative",
        styleTransfer: "Style Transfer",
        
        // 文生图
        textToImageTitle: "Text to Image Generation",
        textPrompt: "Description Text",
        textPromptPlaceholder: "Please enter image description, e.g., a cute cat sleeping in the sun",
        imageStyle: "Style Selection",
        customStyle: "Custom Style Instruction",
        customStylePlaceholder: "e.g., cyberpunk style + ink painting brush strokes",
        generateImage: "Generate Image",
        clearImage: "Clear",
        generating: "Generating, please wait...",
        generationResult: "Generation Result",
        
        // 图生文
        imageToTextTitle: "Image to Text Generation",
        uploadImage: "Upload Image",
        uploadPlaceholder: "Click or drag image here to upload",
        uploadFormat: "Supports JPG, PNG, WebP formats",
        generateText: "Generate Description",
        clearText: "Clear",
        
        // 动态叙事
        dynamicNarrativeTitle: "Dynamic Narrative Generation",
        storyKeywords: "Keywords",
        storyKeywordsPlaceholder: "Please enter keywords, separated by commas, e.g., adventure, forest, mysterious creature",
        storyStyle: "Story Style",
        storyLength: "Story Length",
        storyStyleOptions: {
            fantasy: "Fantasy",
            "sci-fi": "Sci-Fi",
            mystery: "Mystery",
            romance: "Romance",
            adventure: "Adventure"
        },
        storyLengthOptions: {
            short: "Short (3-5 scenes)",
            medium: "Medium (5-8 scenes)",
            long: "Long (8-12 scenes)"
        },
        generateStory: "Generate Story",
        clearStory: "Clear",
        storyPreview: "Story Preview",
        timelineEdit: "Timeline Edit",
        
        // 风格迁移
        styleTransferTitle: "Style Transfer Control",
        uploadOriginalImage: "Upload Original Image",
        styleInstruction: "Style Instruction",
        styleInstructionPlaceholder: "Please enter style instruction, e.g., convert this painting to Van Gogh starry night style",
        transferStyle: "Style Transfer",
        clearStyle: "Clear",
        styleTransferResult: "Style Transfer Result",
        
        // 智能助手
        smartAssistant: "Smart Assistant",
        assistantGreeting: "Hello! I am the smart assistant of the cross-modal content generation system. How can I help you?",
        chatPlaceholder: "Enter your question...",
        send: "Send",
        
        // 登录/注册
        loginRegister: "User Login/Register",
        login: "Login",
        register: "Register",
        username: "Username",
        password: "Password",
        email: "Email",
        confirmPassword: "Confirm Password",
        loginSuccess: "Login successful",
        registerSuccess: "Registration successful, please login",
        loginError: "Username or password error",
        registerError: "Registration failed, please try again",
        logout: "Logout",
        
        // 风格预设
        stylePresets: [
            "Realistic Style",
            "Cartoon Style",
            "Oil Painting Style",
            "Watercolor Style",
            "Cyberpunk",
            "Chinese Style"
        ],
        
        // 提示信息
        pleaseEnterPrompt: "Please enter description text",
        pleaseUploadImage: "Please upload image first",
        pleaseEnterKeywords: "Please enter keywords",
        generationFailed: "Generation failed, please check if the backend service is running",
        
        // 成功消息
        imageGenerated: "Image generated for you: ",
        textGenerated: "Image description generated for you",
        
        // 语言选择
        languages: {
            zh: "中文",
            en: "English",
            ja: "日本語"
        }
    },
    ja: {
        // 页面标题
        title: "クロスモーダルコンテンツ生成システム",
        subtitle: "LLMエンハンスドバージョン - テキストから画像 · 画像からテキスト · 動的ナラティブ · スタイル制御",
        
        // 标签页
        textToImage: "テキストから画像",
        imageToText: "画像からテキスト",
        dynamicNarrative: "動的ナラティブ",
        styleTransfer: "スタイル転送",
        
        // 文生图
        textToImageTitle: "テキストから画像生成",
        textPrompt: "説明テキスト",
        textPromptPlaceholder: "画像の説明を入力してください。例：太陽の下で眠っている可愛い猫",
        imageStyle: "スタイル選択",
        customStyle: "カスタムスタイル指示",
        customStylePlaceholder: "例：サイバーパンクスタイル＋墨絵の筆遣い",
        generateImage: "画像を生成",
        clearImage: "クリア",
        generating: "生成中、お待ちください...",
        generationResult: "生成結果",
        
        // 图生文
        imageToTextTitle: "画像からテキスト生成",
        uploadImage: "画像をアップロード",
        uploadPlaceholder: "ここをクリックまたは画像をドラッグしてアップロード",
        uploadFormat: "JPG、PNG、WebP形式をサポート",
        generateText: "説明を生成",
        clearText: "クリア",
        
        // 动态叙事
        dynamicNarrativeTitle: "動的ナラティブ生成",
        storyKeywords: "キーワード",
        storyKeywordsPlaceholder: "キーワードを入力してください、コンマで区切ります。例：冒険, 森, 神秘的な生き物",
        storyStyle: "ストーリースタイル",
        storyLength: "ストーリーの長さ",
        storyStyleOptions: {
            fantasy: "ファンタジー",
            "sci-fi": "SF",
            mystery: "ミステリー",
            romance: "ロマンス",
            adventure: "冒険"
        },
        storyLengthOptions: {
            short: "短編（3-5シーン）",
            medium: "中篇（5-8シーン）",
            long: "長編（8-12シーン）"
        },
        generateStory: "ストーリーを生成",
        clearStory: "クリア",
        storyPreview: "ストーリープレビュー",
        timelineEdit: "タイムライン編集",
        
        // 风格迁移
        styleTransferTitle: "スタイル転送制御",
        uploadOriginalImage: "元の画像をアップロード",
        styleInstruction: "スタイル指示",
        styleInstructionPlaceholder: "スタイル指示を入力してください。例：この絵をファンゴッホの星月夜スタイルに変換",
        transferStyle: "スタイル転送",
        clearStyle: "クリア",
        styleTransferResult: "スタイル転送結果",
        
        // 智能助手
        smartAssistant: "スマートアシスタント",
        assistantGreeting: "こんにちは！クロスモーダルコンテンツ生成システムのスマートアシスタントです。どのようにお手伝いできますか？",
        chatPlaceholder: "質問を入力...",
        send: "送信",
        
        // 登录/注册
        loginRegister: "ユーザーログイン/登録",
        login: "ログイン",
        register: "登録",
        username: "ユーザー名",
        password: "パスワード",
        email: "メール",
        confirmPassword: "パスワードを確認",
        loginSuccess: "ログイン成功",
        registerSuccess: "登録成功、ログインしてください",
        loginError: "ユーザー名またはパスワードエラー",
        registerError: "登録に失敗しました、もう一度お試しください",
        logout: "ログアウト",
        
        // 风格预设
        stylePresets: [
            "写実的なスタイル",
            "アニメーションスタイル",
            "油絵スタイル",
            "水彩スタイル",
            "サイバーパンク",
            "中国風"
        ],
        
        // 提示信息
        pleaseEnterPrompt: "説明テキストを入力してください",
        pleaseUploadImage: "まず画像をアップロードしてください",
        pleaseEnterKeywords: "キーワードを入力してください",
        generationFailed: "生成に失敗しました、バックエンドサービスが実行されているか確認してください",
        
        // 成功消息
        imageGenerated: "あなたのために画像を生成しました：",
        textGenerated: "画像の説明を生成しました",
        
        // 语言选择
        languages: {
            zh: "中文",
            en: "English",
            ja: "日本語"
        }
    }
};

// 导出i18n对象
if (typeof module !== 'undefined' && module.exports) {
    module.exports = i18n;
} else if (typeof window !== 'undefined') {
    window.i18n = i18n;
}