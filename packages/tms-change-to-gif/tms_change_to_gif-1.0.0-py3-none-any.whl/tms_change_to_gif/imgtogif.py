import glob
from PIL import Image

class GifConverter:
    def __init__(self, path_in=None, path_out=None, resize=(320, 240)):
        """
        path_in  : 원본 여러 이미지 경로(Ex : images/*.png)
        path_out : 결과 이미지 경로(Ex : output/filename.png)
        resize   : 리사이징 크기((320,240))
        """
        self.path_in = path_in or './*.png'
        self.path_out = path_out or './output.gif'
        self.resize = resize
    
    def convert_gif(self):
        """
        GIF 이미지 변환 기능 수행
        """
        # 경로, 사이즈 확인
        print(self.path_in, self.path_out, self.resize)

        '''
        Image.ANTIALIAS는 이미지 리사이징 시 이미지 왜곡을 보정해 품질을 높이기 위한 옵션, 
        하지만, Image.Resampling.LANCZOS로 대체됨
        '''
        img, *images = \
        [Image.open(f).resize(self.resize, Image.Resampling.LANCZOS) for f in sorted(glob.glob(self.path_in))]
        try:
            img.save(
                fp=self.path_out, 
                format='GIF', 
                append_images=images,
                save_all=True, 
                duration=500, 
                loop=0
            )
        except IOError:
            print("Cannot convert!", img)
         
if __name__ == "__main__":
    # 클래스 테스트
    c = GifConverter("./project/images/*.png", './project/image_out/result7.gif', (320,240))
    # 변환
    c.convert_gif()