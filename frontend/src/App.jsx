import React, { useState } from 'react';
import './App.css';

function App() {
    const [idea, setIdea] = useState('');
    const [imagePrompts, setImagePrompts] = useState([]);
    const [selectedImagePrompt, setSelectedImagePrompt] = useState('');
    const [generatedImages, setGeneratedImages] = useState([]);
    const [selectedImage, setSelectedImage] = useState('');
    const [videoPrompt, setVideoPrompt] = useState('');
    const [optimisedVideoPrompt, setOptimisedVideoPrompt] = useState('');
    const [generatedVideo, setGeneratedVideo] = useState('');
    const [loading, setLoading] = useState('');

    const handleGenerateImagePrompts = async () => {
        if (!idea) return alert('请输入您的想法！');
        setLoading('生成图片提示词中...');
        try {
            const response = await fetch('/api/generate-image-prompts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ idea }),
            });
            const data = await response.json();
            const parsedData = typeof data === 'string' ? JSON.parse(data) : data;
            setImagePrompts(parsedData.prompts || []);
        } catch (error) {
            console.error('Error generating image prompts:', error);
            alert('生成图片提示词失败，请检查控制台');
        } finally {
            setLoading('');
        }
    };

    const handleGenerateImages = async () => {
        if (!selectedImagePrompt) return alert('请选择一个图片提示词！');
        setLoading('生成图片中，预计需要1-2分钟...');
        try {
            const response = await fetch('/api/generate-images', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: selectedImagePrompt }),
            });
            const data = await response.json();
            setGeneratedImages(data.output?.results || []);
        } catch (error) {
            console.error('Error generating images:', error);
            alert('生成图片失败，请检查控制台');
        } finally {
            setLoading('');
        }
    };

    const handleOptimiseVideoPrompt = async () => {
        if (!videoPrompt) return alert('请输入视频动态描述！');
        setLoading('优化视频提示词中...');
        try {
            const response = await fetch('/api/optimise-video-prompt', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: videoPrompt }),
            });
            const data = await response.json();
            const parsedData = typeof data === 'string' ? JSON.parse(data) : data;
            setOptimisedVideoPrompt(parsedData.optimised_prompt || '');
        } catch (error) {
            console.error('Error optimising video prompt:', error);
            alert('优化视频提示词失败，请检查控制台');
        } finally {
            setLoading('');
        }
    };

    const handleGenerateVideo = async () => {
        const finalVideoPrompt = optimisedVideoPrompt || videoPrompt;
        if (!selectedImage || !finalVideoPrompt) return alert('请选择图片和输入视频提示词！');
        setLoading('生成视频中，预计需要3-5分钟...');
        try {
            const response = await fetch('/api/generate-video', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image_url: selectedImage, prompt: finalVideoPrompt }),
            });
            const data = await response.json();
            setGeneratedVideo(data.output?.video_url || '');
        } catch (error) {
            console.error('Error generating video:', error);
            alert('生成视频失败，请检查控制台');
        } finally {
            setLoading('');
        }
    };

    return (
        <div className="App">
            <h1>AI 视频创作工作流</h1>
            {loading && <div className="loading">{loading}</div>}

            <div className="workflow-step">
                <h2>第一步：输入您的想法</h2>
                <input
                    type="text"
                    value={idea}
                    onChange={(e) => setIdea(e.target.value)}
                    placeholder="例如：一只戴墨镜的猫在沙滩上"
                />
                <button onClick={handleGenerateImagePrompts}>生成图片提示词</button>
            </div>

            {imagePrompts.length > 0 && (
                <div className="workflow-step">
                    <h2>第二步：选择一个图片提示词</h2>
                    <div className="prompt-selection">
                        {imagePrompts.map((prompt, index) => (
                            <div key={index} className={`prompt-option ${selectedImagePrompt === prompt ? 'selected' : ''}`}>
                                <input
                                    type="radio"
                                    id={`prompt-${index}`}
                                    name="imagePrompt"
                                    value={prompt}
                                    checked={selectedImagePrompt === prompt}
                                    onChange={(e) => setSelectedImagePrompt(e.target.value)}
                                />
                                <label htmlFor={`prompt-${index}`}>{prompt}</label>
                            </div>
                        ))}
                    </div>
                    <button onClick={handleGenerateImages}>生成图片</button>
                </div>
            )}

            {generatedImages.length > 0 && (
                <div className="workflow-step">
                    <h2>第三步：选择一张图片</h2>
                    <div className="image-selection">
                        {generatedImages.map((image, index) => (
                            <img
                                key={index}
                                src={image.url}
                                alt={`Generated Image ${index + 1}`}
                                className={selectedImage === image.url ? 'selected' : ''}
                                onClick={() => setSelectedImage(image.url)}
                            />
                        ))}
                    </div>
                </div>
            )}

            {selectedImage && (
                <div className="workflow-step">
                    <h2>第四步：输入视频动态描述</h2>
                    <input
                        type="text"
                        value={videoPrompt}
                        onChange={(e) => setVideoPrompt(e.target.value)}
                        placeholder="例如：海浪轻轻拍打，猫的尾巴在摇摆"
                    />
                    <button onClick={handleOptimiseVideoPrompt}>优化提示词</button>
                    {optimisedVideoPrompt && (
                        <div>
                            <h4>优化后的提示词：</h4>
                            <p>{optimisedVideoPrompt}</p>
                        </div>
                    )}
                    <button onClick={handleGenerateVideo}>生成视频</button>
                </div>
            )}

            {generatedVideo && (
                <div className="workflow-step">
                    <h2>第五步：查看生成的视频</h2>
                    <video src={generatedVideo} controls />
                </div>
            )}
        </div>
    );
}

export default App;

